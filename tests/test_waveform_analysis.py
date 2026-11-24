import csv
from sequential_logic import ClockedCircuit
from waveform_analysis import recorded,window,write_csv


def test_event_ids_and_rising_edges():
    m=ClockedCircuit("D")
    m.set_input("D",1);m.pulse();m.set_input("D",0);m.pulse()
    names,rows=recorded(m)
    assert names==("CLK","D","Q","Qbar")
    assert [r.number for r in rows]==list(range(7))
    assert [r.number for r in rows if r.rising]==[2,5]
    assert rows[2].values==(1,1,1,0)
    assert rows[5].values==(1,0,0,1)
    assert [r.number for r in window(rows,3)]==[4,5,6]
    assert [r.number for r in window(rows,3,-10)]==[0,1,2]


def test_bounded_history_and_csv(tmp_path):
    m=ClockedCircuit("COUNT4")
    m.set_input("EN",1)
    for _ in range(100):m.pulse()
    names,rows=recorded(m)
    assert len(rows)==64 and rows[-1].number==201
    assert rows[0].number==138
    assert not rows[0].rising # preceding event is no longer retained
    assert window(rows,8,140)[0].number==140
    before=(m.value,m.clock,tuple(m.history),m.sample_count)
    target=tmp_path/"wave.csv";write_csv(m,target)
    with target.open(newline="",encoding="utf-8") as f:data=list(csv.reader(f))
    assert data[0]==["event_index","rising_edge",*names]
    assert data[-1]==[str(rows[-1].number),"0",*map(str,rows[-1].values)]
    assert (m.value,m.clock,tuple(m.history),m.sample_count)==before
    m.reset();assert recorded(m)[1][0].number==0
