"""Instruction-level Mano CPU with actual timing-group snapshots; no GUI or network.

Only named instructions are accepted, not combined register-reference bits.
Interrupts are modeled at instruction boundaries, not clock-cycle timing.
"""
from dataclasses import dataclass
from mano_isa import FIXED_BY_CODE, MEMORY_BY_CODE
from word_arithmetic import alu


@dataclass(frozen=True)
class MicroEvent:
    timing: int
    phase: str
    rtl: str
    before: dict
    after: dict
    reads: tuple
    writes: tuple


@dataclass(frozen=True)
class StepEvent:
    address: int
    word: int
    mnemonic: str
    effective_address: int | None
    before: dict
    after: dict
    writes: tuple
    microevents: tuple = ()


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
        """Complete one instruction atomically at the public boundary.

        Each recorded group is produced by the actual assignments below,
        not by replaying a second simulator. Invalid opcodes leave state intact.
        """
        if self.halted:
            return None
        before = self.registers()
        address = self.pc
        writes, reads, groups = [], [], []
        prior = before
        wi = ri = 0

        def read(a):
            v=self.memory[a]
            reads.append((a,v))
            return v

        def store(a,v):
            writes.append((a,self.memory[a],v))
            self.memory[a]=v

        def mark(timing,phase,rtl):
            nonlocal prior,wi,ri
            after=self.registers()
            groups.append(MicroEvent(timing,phase,rtl,prior,after,tuple(reads[ri:]),tuple(writes[wi:])))
            prior=after
            wi,ri=len(writes),len(reads)

        def finish(word,op,effective):
            return StepEvent(address,word,op,effective,before,self.registers(),tuple(writes),tuple(groups))

        if self.ien and (self.fgi or self.fgo):
            self.tr=self.pc
            self.ar=0
            mark(0,"interrupt","AR ← 0, TR ← PC")
            store(0,self.tr)
            self.pc=0
            mark(1,"interrupt","M[AR] ← TR, PC ← 0")
            self.pc,self.ien=1,0
            mark(2,"interrupt","PC ← PC + 1, IEN ← 0")
            return finish(0,"INT",0)

        # Preflight instruction validity without recording an architectural read.
        word=self.memory[address]
        opcode=(word>>12)&7
        op=MEMORY_BY_CODE[opcode] if opcode<7 else FIXED_BY_CODE.get(word)
        if op is None:
            raise ValueError(f"Unsupported instruction {word:04X} at {address:03X}")
        self.ar=self.pc
        mark(0,"fetch","AR ← PC")
        self.ir=read(self.ar)
        self.pc=(self.pc+1)&0xFFF
        mark(1,"fetch","IR ← M[AR], PC ← PC + 1")
        self.ar=self.ir&0xFFF
        mark(2,"decode","AR ← IR(0–11), decode opcode and I")
        effective=None
        if opcode<7:
            if word&0x8000:
                self.ar=read(self.ar)&0xFFF
                mark(3,"indirect","AR ← M[AR](0–11)")
            else:
                mark(3,"direct","Direct address — no register transfer")
            effective=a=self.ar
            if op in ("AND","ADD","LDA","ISZ"):
                self.dr=read(a)
                mark(4,"execute","DR ← M[AR]")
            if op=="AND":
                self.ac=alu("AND",self.ac,self.dr).word
                mark(5,"execute","AC ← AC ∧ DR")
            elif op=="ADD":
                result=alu("ADD",self.ac,self.dr)
                self.ac,self.e=result.word,result.carry
                mark(5,"execute","AC ← AC + DR, E ← Cout")
            elif op=="LDA":
                self.ac=self.dr
                mark(5,"execute","AC ← DR")
            elif op=="STA":
                store(a,self.ac)
                mark(4,"execute","M[AR] ← AC")
            elif op=="BUN":
                self.pc=a
                mark(4,"execute","PC ← AR")
            elif op=="BSA":
                store(a,self.pc)
                self.ar=(a+1)&0xFFF
                mark(4,"execute","M[AR] ← PC, AR ← AR + 1")
                self.pc=self.ar
                mark(5,"execute","PC ← AR")
            elif op=="ISZ":
                self.dr=(self.dr+1)&0xFFFF
                mark(5,"execute","DR ← DR + 1")
                store(a,self.dr)
                if not self.dr:self.pc=(self.pc+1)&0xFFF
                mark(6,"execute","M[AR] ← DR; if DR = 0: PC ← PC + 1")
        else:
            rtl=""
            if op=="CLA":self.ac=0;rtl="AC ← 0"
            elif op=="CLE":self.e=0;rtl="E ← 0"
            elif op=="CMA":self.ac=alu("NOT",self.ac).word;rtl="AC ← ¬AC"
            elif op=="CME":self.e^=1;rtl="E ← ¬E"
            elif op in ("CIR","CIL"):
                result=alu(op,self.ac,carry_in=self.e)
                self.ac,self.e=result.word,result.carry
                rtl="(E, AC) ← "+op+"(E, AC)"
            elif op=="INC":self.ac=alu("INC",self.ac).word;rtl="AC ← AC + 1"
            elif op in ("SPA","SNA","SZA","SZE","SKI","SKO"):
                conditions={"SPA":("AC(15) = 0",not self.ac&0x8000),"SNA":("AC(15) = 1",bool(self.ac&0x8000)),
                    "SZA":("AC = 0",self.ac==0),"SZE":("E = 0",self.e==0),"SKI":("FGI = 1",self.fgi==1),"SKO":("FGO = 1",self.fgo==1)}
                condition,taken=conditions[op]
                if taken:self.pc=(self.pc+1)&0xFFF
                rtl="if "+condition+": PC ← PC + 1"
            elif op=="HLT":self.halted=True;rtl="S ← 0"
            elif op=="INP":self.ac,self.fgi=(self.ac&0xFF00)|self.inpr,0;rtl="AC(0–7) ← INPR, FGI ← 0"
            elif op=="OUT":self.outr,self.fgo=self.ac&0xFF,0;rtl="OUTR ← AC(0–7), FGO ← 0"
            elif op=="ION":self.ien=1;rtl="IEN ← 1"
            elif op=="IOF":self.ien=0;rtl="IEN ← 0"
            mark(3,"io" if word&0x8000 else "register",rtl)
        return finish(word,op,effective)
