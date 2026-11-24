"""Three-stage arithmetic pipeline: LOAD, MUL, ADD/ACC.

Ideal unit-latency stages, one job per cycle, modular 16-bit words.
The accumulator is keyed by output element, allowing vector and matrix
operations to share a single arithmetic pipeline.
"""
from dataclasses import dataclass
import re

MASK=65535


def word(value):
    if not isinstance(value,int) or not -32768<=value<=65535:
        raise ValueError("Expected a 16-bit word")
    return value&MASK


def parse_matrix(text):
    if len(text)>4096:raise ValueError("Input too long")
    rows=[]
    for line in text.strip().splitlines():
        if not line.strip():continue
        tokens=re.split(r"[\s,]+",line.strip())
        if any(not re.fullmatch(r"[+-]?[0-9]{1,5}",t) for t in tokens):
            raise ValueError("Invalid decimal word")
        rows.append(tuple(word(int(t)) for t in tokens))
    return matrix(rows)


def matrix(rows):
    rows=tuple(tuple(word(v) for v in row) for row in rows)
    if not 1<=len(rows)<=8 or not 1<=len(rows[0])<=8 or any(len(r)!=len(rows[0]) for r in rows):
        raise ValueError("Expected rectangular matrix, 1–8 rows and columns")
    return rows


@dataclass(frozen=True)
class Job:
    index:tuple
    output:tuple
    a:int
    b:int
    c:int=0


@dataclass(frozen=True)
class Product:
    job:Job
    value:int


@dataclass(frozen=True)
class ArithmeticCycle:
    number:int
    load:Job | None
    multiply:Product | None
    accumulate:Product | None
    before:int | None
    after:int | None


class ArithmeticPipeline:
    def __init__(self,jobs,shape):
        self.jobs=tuple(jobs)
        if not self.jobs:raise ValueError("No arithmetic jobs")
        self.shape=shape
        self.results={(r,c):0 for r in range(shape[0]) for c in range(shape[1])}
        self.cursor=0
        self.loaded=None
        self.product=None
        self.cycles=0

    @property
    def done(self):
        return self.cursor==len(self.jobs) and self.loaded is None and self.product is None

    def step(self):
        if self.done:return None
        load=self.jobs[self.cursor] if self.cursor<len(self.jobs) else None
        if load is not None:self.cursor+=1
        multiply=Product(self.loaded,(self.loaded.a*self.loaded.b)&MASK) if self.loaded is not None else None
        accumulate=self.product
        before=after=None
        if accumulate is not None:
            job=accumulate.job
            before=self.results[job.output]
            after=(before+accumulate.value+job.c)&MASK
            self.results[job.output]=after
        self.loaded,self.product=load,multiply
        self.cycles+=1
        return ArithmeticCycle(self.cycles,load,multiply,accumulate,before,after)

    def run(self):
        trace=[]
        while not self.done:trace.append(self.step())
        return tuple(trace)

    def output(self):
        return tuple(tuple(self.results[r,c] for c in range(self.shape[1])) for r in range(self.shape[0]))


def build_pipeline(mode,a,b,c=None):
    a,b=matrix(a),matrix(b)
    jobs=[]
    if mode=="matrix":
        if len(a[0])!=len(b):raise ValueError("Incompatible matrix dimensions")
        shape=(len(a),len(b[0]))
        for i in range(shape[0]):
            for j in range(shape[1]):
                for k in range(len(b)):
                    jobs.append(Job((i,j,k),(i,j),a[i][k],b[k][j]))
    else:
        if mode not in ("add","sub","mul","mac","dot"):raise ValueError("Unknown vector operation")
        if len(a)!=1 or len(b)!=1 or len(a[0])!=len(b[0]):
            raise ValueError("Expected equal-length row vectors")
        n=len(a[0])
        if mode=="mac":
            c=matrix(c or ())
            if len(c)!=1 or len(c[0])!=n:raise ValueError("Expected equal-length C")
        shape=(1,1 if mode=="dot" else n)
        for i,(x,y) in enumerate(zip(a[0],b[0])):
            output=(0,0 if mode=="dot" else i)
            if mode=="add":job=Job((i,),output,x,1,y)
            elif mode=="sub":job=Job((i,),output,x,1,(-y)&MASK)
            else:job=Job((i,),output,x,y,c[0][i] if mode=="mac" else 0)
            jobs.append(job)
    return ArithmeticPipeline(jobs,shape)
