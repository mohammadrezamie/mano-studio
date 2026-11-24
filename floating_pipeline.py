"""Ideal four-stage binary16 ADD/SUB arithmetic pipeline.

Compare exponents, align signed significands exactly, add, normalize/round.
Finite alignment preserves every discarded bit with Fraction. Shared binary16
encoder provides the single rounding decision; existing ALU handles specials.
Not a gate-level FPU or Mano's historical floating-point encoding.
"""
from dataclasses import dataclass
from fractions import Fraction
import re
from floating_arithmetic import Half, FloatResult, decode_half, encode_half, float_alu, power2


@dataclass(frozen=True)
class Job:
    op:str
    a:int
    b:int


@dataclass(frozen=True)
class Compared:
    number:int
    job:Job
    a:Half
    b:Half
    exponent:int | None
    shifts:tuple


@dataclass(frozen=True)
class Aligned:
    compared:Compared
    left:Fraction | None
    right:Fraction | None


@dataclass(frozen=True)
class Summed:
    aligned:Aligned
    significand:Fraction | None
    exact:Fraction | None
    zero_sign:int


@dataclass(frozen=True)
class Completed:
    summed:Summed
    result:FloatResult


@dataclass(frozen=True)
class Cycle:
    number:int
    compare:Compared | None
    align:Aligned | None
    add:Summed | None
    round:Completed | None


def compare(number,job):
    if job.op not in ("ADD","SUB"):
        raise ValueError("Expected ADD or SUB")
    a=decode_half(job.a)
    b=decode_half(job.b ^ (0x8000 if job.op=="SUB" else 0))
    if a.value is None or b.value is None:
        return Compared(number,job,a,b,None,())
    ea,eb=max(a.exponent,1)-15,max(b.exponent,1)-15
    e=max(ea,eb)
    return Compared(number,job,a,b,e,(e-ea,e-eb))


def align(c):
    if c.exponent is None:return Aligned(c,None,None)
    # Values divided by common 2**e yield exact signed significands,
    # equivalent to right shifting each original significand by its delta.
    scale=power2(c.exponent)
    return Aligned(c,c.a.value/scale,c.b.value/scale)


def add(a):
    c=a.compared
    if a.left is None:return Summed(a,None,None,0)
    significand=a.left+a.right
    zero_sign=int(c.a.kind==c.b.kind=="zero" and c.a.sign==c.b.sign==1)
    return Summed(a,significand,significand*power2(c.exponent),zero_sign)


def finish(s):
    job=s.aligned.compared.job
    r=float_alu(job.op,job.a,job.b) if s.exact is None else encode_half(s.exact,s.zero_sign)
    return Completed(s,r)


class FloatPipeline:
    def __init__(self,jobs):
        self.jobs=tuple(jobs)
        if not 1<=len(self.jobs)<=128:raise ValueError("Expected 1–128 jobs")
        for job in self.jobs:
            if job.op not in ("ADD","SUB") or any(type(v) is not int or not 0<=v<=65535 for v in (job.a,job.b)):
                raise ValueError("Invalid binary16 job")
        self.cursor=0
        self.compared=self.aligned=self.summed=None
        self.cycles=0
        self.results=[]

    @property
    def done(self):
        return self.cursor==len(self.jobs) and not any((self.compared,self.aligned,self.summed))

    def step(self):
        if self.done:return None
        # All stage inputs come from the preceding clock, never from a
        # result produced by another stage in this clock.
        c=compare(self.cursor+1,self.jobs[self.cursor]) if self.cursor<len(self.jobs) else None
        a=align(self.compared) if self.compared is not None else None
        s=add(self.aligned) if self.aligned is not None else None
        r=finish(self.summed) if self.summed is not None else None
        if c is not None:self.cursor+=1
        if r is not None:self.results.append(r)
        self.compared,self.aligned,self.summed=c,a,s
        self.cycles+=1
        return Cycle(self.cycles,c,a,s,r)

    def run(self):
        trace=[]
        while not self.done:trace.append(self.step())
        return tuple(trace)


EXAMPLE="""ADD 3C00 3800
SUB 4000 3C00
ADD 3C00 1000
ADD 0001 0001
ADD 7BFF 7BFF
ADD 7C00 FC00"""


def parse_jobs(text):
    if len(text)>8192:raise ValueError("Input too long")
    jobs=[]
    for i,raw in enumerate(text.splitlines(),1):
        line=raw.split("#",1)[0].strip().upper()
        if not line:continue
        m=re.fullmatch(r"(ADD|SUB)\s+([0-9A-F]{4})[\s,]+([0-9A-F]{4})",line)
        if not m:raise ValueError(f"Invalid job at line {i}")
        jobs.append(Job(m[1],int(m[2],16),int(m[3],16)))
    if not 1<=len(jobs)<=128:raise ValueError("Expected 1–128 jobs")
    return tuple(jobs)
