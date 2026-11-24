"""Five-stage in-order educational pipeline, separate from Mano Basic Computer.

IF/ID/EX/MEM/WB, word-addressed data memory, R0 hardwired zero.
Separate instruction/data memory, single-cycle ALU and data memory,
WB writes before ID/EX reads. Branches resolve in EX; no delay slot.
"""
from dataclasses import dataclass, replace
import re
from word_arithmetic import alu

ALU_OPS=("ADD","SUB","AND","OR","XOR")
EXAMPLE="""ADDI R1, R0, 5
ST R1, R0, 16
LD R2, R0, 16
ADD R3, R2, R1
BEQ R3, R3, DONE
ADDI R4, R0, 99
DONE: SUB R5, R3, R1"""


@dataclass(frozen=True)
class Instruction:
    op:str
    dest:int=0
    sources:tuple=()
    immediate:int=0
    target:int=0
    text:str=""


def parse_program(source):
    if len(source)>8192:raise ValueError("Program too long")
    labels={};rows=[]
    for line,raw in enumerate(source.splitlines(),1):
        text=raw.split("#",1)[0].strip().upper()
        if not text:continue
        if ":" in text:
            label,text=(s.strip() for s in text.split(":",1))
            if not re.fullmatch(r"[A-Z_][A-Z0-9_]*",label) or label in labels:
                raise ValueError(f"Invalid label at line {line}")
            labels[label]=len(rows)
        if text:rows.append((line,text))
    if not 1<=len(rows)<=128:raise ValueError("Expected 1–128 instructions")
    def reg(s):
        if not re.fullmatch(r"R[0-7]",s):raise ValueError("Invalid register")
        return int(s[1])
    def imm(s):
        if not re.fullmatch(r"[+-]?[0-9]{1,5}",s):raise ValueError("Invalid immediate")
        n=int(s)
        if not -32768<=n<=32767:raise ValueError("Immediate out of range")
        return n
    program=[]
    for line,text in rows:
        parts=text.split(None,1);op=parts[0]
        args=[s.strip() for s in parts[1].split(",")] if len(parts)>1 else []
        try:
            if op in ALU_OPS and len(args)==3:
                ins=Instruction(op,reg(args[0]),(reg(args[1]),reg(args[2])),text=text)
            elif op in ("ADDI","LD") and len(args)==3:
                ins=Instruction(op,reg(args[0]),(reg(args[1]),),imm(args[2]),text=text)
            elif op=="ST" and len(args)==3:
                ins=Instruction(op,0,(reg(args[0]),reg(args[1])),imm(args[2]),text=text)
            elif op=="BEQ" and len(args)==3 and args[2] in labels and labels[args[2]]<len(rows):
                ins=Instruction(op,0,(reg(args[0]),reg(args[1])),target=labels[args[2]],text=text)
            elif op=="NOP" and not args:
                ins=Instruction(op,text=text)
            else:raise ValueError("Invalid instruction")
        except ValueError as error:
            raise ValueError(f"Line {line}: {error}") from error
        program.append(ins)
    return tuple(program)


@dataclass(frozen=True)
class Slot:
    pc:int
    ins:Instruction
    value:int=0
    address:int=0


@dataclass(frozen=True)
class Cycle:
    number:int
    stages:tuple
    stall:bool
    flushed:tuple
    forwarded:tuple
    retired:int | None
    registers:tuple
    writes:tuple


class Pipeline:
    def __init__(self,program,forwarding=True,memory=None):
        self.program=tuple(program)
        if not self.program:raise ValueError("Empty program")
        self.forwarding=forwarding
        self.registers=[0]*8
        self.memory=dict(memory or {})
        if any(not 0<=a<=65535 or not 0<=v<=65535 for a,v in self.memory.items()):
            raise ValueError("Invalid data memory")
        self.pc=0
        self.stages=[self.fetch(),None,None,None,None]
        self.cycles=0;self.retired=0;self.stalls=0;self.flushes=0

    def fetch(self):
        if self.pc>=len(self.program):return None
        slot=Slot(self.pc,self.program[self.pc]);self.pc+=1
        return slot

    @property
    def done(self):return not any(self.stages)

    def step(self):
        if self.done:return None
        if self.cycles>=512:raise ValueError("Cycle limit reached")
        f,d,e,m,w=self.stages
        self.cycles+=1
        writes=[];forwarded=[];flushed=()
        if w:
            if w.ins.dest:self.registers[w.ins.dest]=w.value
            self.retired+=1
        next_w=m
        if m:
            if m.ins.op=="LD":next_w=replace(m,value=self.memory.get(m.address,0))
            elif m.ins.op=="ST":
                self.memory[m.address]=m.value
                writes.append((m.address,m.value))
        def operand(reg):
            if reg and self.forwarding and m and m.ins.dest==reg:
                if m.ins.op=="LD":raise RuntimeError("Missing load-use interlock")
                forwarded.append((reg,m.pc,"MEM"))
                return m.value
            if reg and self.forwarding and w and w.ins.dest==reg:
                forwarded.append((reg,w.pc,"WB"))
            return self.registers[reg]
        next_m=e;branch=None
        if e:
            ins=e.ins
            values=tuple(operand(r) for r in ins.sources)
            if ins.op in ALU_OPS:next_m=replace(e,value=alu(ins.op,*values).word)
            elif ins.op=="ADDI":next_m=replace(e,value=(values[0]+ins.immediate)&65535)
            elif ins.op=="LD":next_m=replace(e,address=(values[0]+ins.immediate)&65535)
            elif ins.op=="ST":next_m=replace(e,value=values[0],address=(values[1]+ins.immediate)&65535)
            elif ins.op=="BEQ" and values[0]==values[1]:branch=ins.target
        stall=False
        if branch is not None:
            flushed=tuple(slot.pc for slot in (d,f) if slot)
            self.flushes+=len(flushed)
            self.pc=branch
            next_f,next_d,next_e=self.fetch(),None,None
        else:
            needed=set(d.ins.sources)-{0} if d else set()
            producers=(e,) if self.forwarding else (e,m)
            stall=any(slot and slot.ins.dest in needed and (not self.forwarding or slot.ins.op=="LD") for slot in producers)
            if stall:
                self.stalls+=1
                next_f,next_d,next_e=f,d,None
            else:next_f,next_d,next_e=self.fetch(),f,d
        self.stages=[next_f,next_d,next_e,next_m,next_w]
        return Cycle(self.cycles,tuple(slot.pc if slot else None for slot in (f,d,e,m,w)),
                     stall,flushed,tuple(forwarded),w.pc if w else None,tuple(self.registers),tuple(writes))

    def run(self):
        rows=[]
        while not self.done:rows.append(self.step())
        return tuple(rows)
