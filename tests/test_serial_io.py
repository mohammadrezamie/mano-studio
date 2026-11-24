import itertools
import pytest
from serial_io import Format,SerialLink,encode,decode


@pytest.mark.parametrize("width,parity,stops",list(itertools.product(range(5,9),("none","even","odd"),(1,2))))
def test_all_payloads(width,parity,stops):
    fmt=Format(width,parity,stops)
    for value in range(1<<width):
        frame=encode(value,fmt)
        assert frame[0]==0 and frame[-stops:]==(1,)*stops
        assert frame[1:width+1]==tuple(value>>i&1 for i in range(width))
        if parity!="none":assert sum(frame[1:width+2])%2==int(parity=="odd")
        result=decode(frame,fmt)
        assert result.ok and result.value==value
        m=SerialLink(fmt);m.start(value);events=m.run()
        assert len(events)==len(frame) and events[-1].queued
        assert m.read()==value and m.step() is None


def test_each_corrupted_bit():
    fmt=Format(8,"even",2)
    for index,label in enumerate(fmt.labels):
        m=SerialLink(fmt);m.start(0xA5,index);events=m.run()
        r=m.result
        assert r.start_error==(label=="START")
        assert r.parity_error==(label.startswith("D") or label=="P")
        assert r.framing_error==label.startswith("STOP")
        assert not r.ok and m.fifo.empty and m.errors==1
        assert sum(e.tx!=e.rx for e in events)==1


def test_no_parity_data_corruption_is_not_detected():
    m=SerialLink();m.start(0xA5,1);m.run()
    assert m.result.ok and m.read()==0xA4


def test_fifo_overrun_and_irq():
    calls=[]
    m=SerialLink(notify=lambda:calls.append("irq"))
    for value in range(5):
        m.start(value);m.run()
    assert m.fifo.contents()==(0,1,2,3)
    assert m.overrun and m.dropped==1 and m.errors==0 and len(calls)==5
    assert m.read()==0
    m.start(6);m.run()
    assert m.fifo.contents()==(1,2,3,6)
    m.start(7,0);m.run()
    assert m.errors==1 and len(calls)==7


def test_rejected_inputs_atomic():
    m=SerialLink()
    for value,flip in ((256,None),(1,10),(-1,None),(1,-1)):
        with pytest.raises(ValueError):m.start(value,flip)
    assert not m.active and not m.events
    m.start(1)
    with pytest.raises(ValueError):m.start(2)
    assert m.active and not m.rx
    with pytest.raises(ValueError):decode((0,1),Format())
