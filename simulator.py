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
    final: bool = False


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
        self._cycle = None
        self._groups = []
        self._context = None
        self.completed_event = None

    def registers(self):
        return {name.upper(): getattr(self, name) for name in
                ("pc","ac","e","ir","ar","dr","tr","inpr","outr","fgi","fgo","ien","halted")}

    def input_byte(self, value):
        if self.in_progress:
            raise ValueError("Finish or rewind the current instruction before I/O")
        if not 0 <= value <= 255:
            raise ValueError("Input must be an 8-bit value")
        if self.fgi:
            raise ValueError("Input register already contains unread data")
        self.inpr, self.fgi = value, 1

    def output_byte(self):
        if self.in_progress:
            raise ValueError("Finish or rewind the current instruction before I/O")
        if self.fgo:
            return None
        self.fgo = 1
        return self.outr

    def _instruction(self):
        """Resumable single execution path for instruction and timing-group stepping.

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
            event=MicroEvent(timing,phase,rtl,prior,after,tuple(reads[ri:]),tuple(writes[wi:]),timing==last_timing)
            groups.append(event)
            prior=after
            wi,ri=len(writes),len(reads)
            return event

        def finish(word,op,effective):
            return StepEvent(address,word,op,effective,before,self.registers(),tuple(writes),tuple(groups))

        if self.ien and (self.fgi or self.fgo):
            last_timing=2
            self._context=(address,0,"INT")
            self.tr=self.pc
            self.ar=0
            yield mark(0,"interrupt","AR ← 0, TR ← PC")
            store(0,self.tr)
            self.pc=0
            yield mark(1,"interrupt","M[AR] ← TR, PC ← 0")
            self.pc,self.ien=1,0
            yield mark(2,"interrupt","PC ← PC + 1, IEN ← 0")
            return finish(0,"INT",0)

        # Preflight instruction validity without recording an architectural read.
        word=self.memory[address]
        opcode=(word>>12)&7
        op=MEMORY_BY_CODE[opcode] if opcode<7 else FIXED_BY_CODE.get(word)
        if op is None:
            raise ValueError(f"Unsupported instruction {word:04X} at {address:03X}")
        last_timing=6 if op=="ISZ" else 5 if op in ("AND","ADD","LDA","BSA") else 4 if opcode<7 else 3
        self._context=(address,word,op)
        self.ar=self.pc
        yield mark(0,"fetch","AR ← PC")
        self.ir=read(self.ar)
        self.pc=(self.pc+1)&0xFFF
        yield mark(1,"fetch","IR ← M[AR], PC ← PC + 1")
        self.ar=self.ir&0xFFF
        yield mark(2,"decode","AR ← IR(0–11), decode opcode and I")
        effective=None
        if opcode<7:
            if word&0x8000:
                self.ar=read(self.ar)&0xFFF
                yield mark(3,"indirect","AR ← M[AR](0–11)")
            else:
                yield mark(3,"direct","Direct address — no register transfer")
            effective=a=self.ar
            if op in ("AND","ADD","LDA","ISZ"):
                self.dr=read(a)
                yield mark(4,"execute","DR ← M[AR]")
            if op=="AND":
                self.ac=alu("AND",self.ac,self.dr).word
                yield mark(5,"execute","AC ← AC ∧ DR")
            elif op=="ADD":
                result=alu("ADD",self.ac,self.dr)
                self.ac,self.e=result.word,result.carry
                yield mark(5,"execute","AC ← AC + DR, E ← Cout")
            elif op=="LDA":
                self.ac=self.dr
                yield mark(5,"execute","AC ← DR")
            elif op=="STA":
                store(a,self.ac)
                yield mark(4,"execute","M[AR] ← AC")
            elif op=="BUN":
                self.pc=a
                yield mark(4,"execute","PC ← AR")
            elif op=="BSA":
                store(a,self.pc)
                self.ar=(a+1)&0xFFF
                yield mark(4,"execute","M[AR] ← PC, AR ← AR + 1")
                self.pc=self.ar
                yield mark(5,"execute","PC ← AR")
            elif op=="ISZ":
                self.dr=(self.dr+1)&0xFFFF
                yield mark(5,"execute","DR ← DR + 1")
                store(a,self.dr)
                if not self.dr:self.pc=(self.pc+1)&0xFFF
                yield mark(6,"execute","M[AR] ← DR; if DR = 0: PC ← PC + 1")
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
            yield mark(3,"io" if word&0x8000 else "register",rtl)
        return finish(word,op,effective)


    @property
    def in_progress(self):
        return self._cycle is not None

    @property
    def pending_event(self):
        if not self.in_progress or not self._groups:
            return None
        address,word,op=self._context
        groups=tuple(self._groups)
        effective=0 if op=="INT" else None
        if op in MEMORY_BY_CODE.values() and len(groups)>=4:
            effective=groups[3].after["AR"]
        return StepEvent(address,word,op,effective,groups[0].before,
                         groups[-1].after,tuple(w for g in groups for w in g.writes),groups)

    def microstep(self):
        """Execute exactly one timing group. A final group publishes StepEvent."""
        self.completed_event=None
        if self._cycle is None:
            if self.halted:return None
            self._groups=[]
            self._cycle=self._instruction()
        try:
            group=next(self._cycle)
        except Exception:
            self.cancel_pending()
            raise
        self._groups.append(group)
        if group.final:
            try:
                next(self._cycle)
            except StopIteration as stop:
                self.completed_event=stop.value
            else:
                raise RuntimeError("Unexpected group after final timing")
            self._cycle=None
            self._groups=[]
            self._context=None
        return group

    def step(self):
        """Complete current or next instruction through the same timing engine."""
        while True:
            group=self.microstep()
            if group is None:return None
            if group.final:return self.completed_event

    def cancel_pending(self):
        """Restore only the register snapshot and written cells of a partial instruction."""
        pending=self.pending_event
        if pending:
            for address,old,_ in reversed(pending.writes):self.memory[address]=old
            for name,value in pending.before.items():setattr(self,name.lower(),value)
        if self._cycle is not None:self._cycle.close()
        self._cycle=None
        self._groups=[]
        self._context=None
        self.completed_event=None
        return pending

    def rewind_group(self):
        """Undo one partial group using bounded replay from the instruction boundary.

        External I/O is prohibited mid-instruction, so replay is deterministic.
        No copied memory image or second execution engine.
        """
        pending=self.cancel_pending()
        if pending is None:return None
        for _ in range(len(pending.microevents)-1):self.microstep()
        return pending.microevents[-1]
