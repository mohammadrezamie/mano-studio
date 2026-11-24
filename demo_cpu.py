"""Educational demonstration of a real four-instruction Mano program.

This is intentionally NOT the general-purpose CPU simulator. Each step is
computed from the example's memory, not from pre-rendered animation frames.
"""
from dataclasses import dataclass


@dataclass
class DemoCPU:
    ac: int = 0
    e: int = 0
    pc: int = 0
    ir: int = 0
    halted: bool = False

    def __post_init__(self):
        self.memory = [0] * 4096
        self.memory[:4] = [0x2100, 0x1101, 0x3102, 0x7001]
        self.memory[0x100] = 5
        self.memory[0x101] = 3
        self.last = ""

    def step(self):
        if self.halted:
            return False
        self.ir = self.memory[self.pc]
        self.pc = (self.pc + 1) & 0xFFF
        address = self.ir & 0xFFF
        opcode = self.ir >> 12
        if opcode == 2:
            self.ac = self.memory[address]
            self.last = "LDA"
        elif opcode == 1:
            total = self.ac + self.memory[address]
            self.ac, self.e = total & 0xFFFF, (total >> 16) & 1
            self.last = "ADD"
        elif opcode == 3:
            self.memory[address] = self.ac
            self.last = "STA"
        elif self.ir == 0x7001:
            self.halted = True
            self.last = "HLT"
        else:
            raise ValueError("Instruction outside the educational demo")
        return True
