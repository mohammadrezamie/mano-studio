"""Instruction-level Mano CPU; no GUI or network dependency.

Only named instructions are accepted, not combined register-reference bits.
Interrupts are modeled at instruction boundaries, not clock-cycle timing.
"""
from dataclasses import dataclass
from mano_isa import FIXED_BY_CODE, MEMORY_BY_CODE
from word_arithmetic import alu


@dataclass(frozen=True)
class StepEvent:
    address: int
    word: int
    mnemonic: str
    effective_address: int | None
    before: dict
    after: dict
    writes: tuple


class CPU:
    def __init__(self, words=None, entry=0):
        if not 0 <= entry <= 0xFFF:
            raise ValueError("Invalid entry")
        self.memory = [0] * 4096
        for address, word in (words or {}).items():
            if not 0 <= address <= 0xFFF or not 0 <= word <= 0xFFFF:
                raise ValueError("Invalid memory image")
            self.memory[address] = word
        self.pc = entry
        self.ac = self.e = self.ir = self.ar = self.dr = self.tr = 0
        self.inpr = self.outr = self.fgi = self.ien = 0
        self.fgo = 1
        self.halted = False

    def registers(self):
        return {name.upper(): getattr(self, name) for name in
                ("pc","ac","e","ir","ar","dr","tr","inpr","outr","fgi","fgo","ien","halted")}

    def input_byte(self, value):
        if not 0 <= value <= 255:
            raise ValueError("Input must be an 8-bit value")
        if self.fgi:
            raise ValueError("Input register already contains unread data")
        self.inpr, self.fgi = value, 1

    def output_byte(self):
        if self.fgo:
            return None
        self.fgo = 1
        return self.outr

    def step(self):
        if self.halted:
            return None
        before = self.registers()
        address = self.pc
        writes = []
        def store(a, v):
            writes.append((a, self.memory[a], v))
            self.memory[a] = v
        if self.ien and (self.fgi or self.fgo):
            self.tr = self.pc
            self.ar = 0
            store(0, self.pc)
            self.pc, self.ien = 1, 0
            return StepEvent(address, 0, "INT", 0, before, self.registers(), tuple(writes))
        word = self.memory[address]
        opcode = (word >> 12) & 7
        op = MEMORY_BY_CODE[opcode] if opcode < 7 else FIXED_BY_CODE.get(word)
        if op is None:
            raise ValueError(f"Unsupported instruction {word:04X} at {address:03X}")
        self.ir = word
        self.pc = (self.pc + 1) & 0xFFF
        self.ar = word & 0xFFF
        effective = None
        if opcode < 7:
            if word & 0x8000:
                self.ar = self.memory[self.ar] & 0xFFF
            effective = a = self.ar
            if op in ("AND", "ADD", "LDA", "ISZ"):
                self.dr = self.memory[a]
            if op == "AND": self.ac = alu("AND",self.ac,self.dr).word
            elif op == "ADD":
                result = alu("ADD",self.ac,self.dr)
                self.ac, self.e = result.word, result.carry
            elif op == "LDA": self.ac = self.dr
            elif op == "STA": store(a, self.ac)
            elif op == "BUN": self.pc = a
            elif op == "BSA":
                store(a, self.pc)
                self.ar = self.pc = (a + 1) & 0xFFF
            elif op == "ISZ":
                self.dr = (self.dr + 1) & 0xFFFF
                store(a, self.dr)
                if not self.dr: self.pc = (self.pc + 1) & 0xFFF
        elif op == "CLA": self.ac = 0
        elif op == "CLE": self.e = 0
        elif op == "CMA": self.ac = alu("NOT",self.ac).word
        elif op == "CME": self.e ^= 1
        elif op in ("CIR", "CIL"):
            result = alu(op,self.ac,carry_in=self.e)
            self.ac,self.e = result.word,result.carry
        elif op == "INC": self.ac = alu("INC",self.ac).word
        elif op in ("SPA", "SNA", "SZA", "SZE", "SKI", "SKO"):
            condition = {"SPA": not self.ac & 0x8000, "SNA": bool(self.ac & 0x8000),
                         "SZA": self.ac == 0, "SZE": self.e == 0,
                         "SKI": self.fgi == 1, "SKO": self.fgo == 1}[op]
            if condition: self.pc = (self.pc + 1) & 0xFFF
        elif op == "HLT": self.halted = True
        elif op == "INP": self.ac, self.fgi = (self.ac & 0xFF00) | self.inpr, 0
        elif op == "OUT": self.outr, self.fgo = self.ac & 0xFF, 0
        elif op == "ION": self.ien = 1
        elif op == "IOF": self.ien = 0
        return StepEvent(address, word, op, effective, before, self.registers(), tuple(writes))
