"""Non-mutating analysis of the clocked circuit's retained event samples."""
import csv
from dataclasses import dataclass


@dataclass(frozen=True)
class RecordedSample:
    number:int
    values:tuple
    rising:bool


def recorded(model):
    names=("CLK",)+model.pins+tuple(model.outputs)
    first=model.sample_count-len(model.history)
    rows=[]
    previous=None
    for i,sample in enumerate(model.history,first):
        rows.append(RecordedSample(i,(sample.clock,)+sample.inputs+sample.outputs,
                                   previous==0 and sample.clock==1))
        previous=sample.clock
    return names,tuple(rows)


def window(rows,length,start=None):
    """Clamp by absolute event number, not deque-relative index."""
    if not rows:return ()
    if type(length) is not int or length<1:raise ValueError("Invalid window")
    length=min(length,len(rows))
    lo,hi=rows[0].number,rows[-length].number
    start=hi if start is None else max(lo,min(hi,start))
    offset=start-lo
    return rows[offset:offset+length]


def write_csv(model,path):
    names,rows=recorded(model)
    with open(path,"w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(("event_index","rising_edge")+names)
        for row in rows:writer.writerow((row.number,int(row.rising))+row.values)
