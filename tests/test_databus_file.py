import pytest
from databus_lab import Databus
from databus_file import snapshot, restore, save, load
import mano_file


def state(m):
    return (dict(m.registers),[m.memory.read(i) for i in range(16)],m.history,m.events)


def test_roundtrip_truncated_history(tmp_path):
    m=Databus()
    for i in range(100):
        m.tick(("EXT",),("AR",),i%16)
        m.tick(("EXT",),("RAM","R0"),(i//2)%16)
        m.tick(("RAM",),("R1",))
    staged=(("R0","R1"),("AR",),3)
    path=tmp_path/"experiment.mano"
    save(path,m,staged)
    recovered,selected=load(path)
    assert state(m)==state(recovered)
    assert selected==staged and len(recovered.history)==64
    m.tick(("EXT",),("RAM","AR"),8)
    recovered.tick(("EXT",),("RAM","AR"),8)
    assert state(m)==state(recovered)


def test_empty_and_idle():
    m=Databus()
    staged=((),(),0)
    restored,selected=restore(snapshot(m,staged))
    assert state(restored)==state(m) and selected==staged
    m.tick((),())
    restored,_=restore(snapshot(m,staged))
    assert restored.history[-1].bus=="ZZZZ"


@pytest.mark.parametrize("key,value", [
    ("registers",[0,0,True]),("ram",[0]*15),("ram",[0]*15+[16]),
    ("events",[{"sources":[],"destinations":[],"external":0}]*65),
    ("events",[{"sources":["R0","R1"],"destinations":["RAM"],"external":0}]),
    ("events",[{"sources":["RAM","RAM"],"destinations":[],"external":0}]),
    ("controls",{"sources":["unknown"],"destinations":[],"external":0}),
    ("controls",{"sources":[{}],"destinations":[],"external":0}),
    ("controls",{"sources":[],"destinations":[],"external":True}),
])
def test_invalid(key,value):
    payload=snapshot(Databus(),((),(),0))
    payload[key]=value
    with pytest.raises(ValueError):
        restore(payload)


def test_wrong_kind(tmp_path):
    path=tmp_path/"text.mano"
    mano_file.save(path,"rtl","AC ← 0")
    with pytest.raises(ValueError):
        load(path)


def test_invalid_save_preserves_previous(tmp_path):
    path=tmp_path/"experiment.mano"
    m=Databus()
    save(path,m,((),(),0))
    original=path.read_bytes()
    with pytest.raises(ValueError):
        save(path,m,(("unknown",),(),0))
    assert path.read_bytes()==original


def test_shipped_native_checkpoint():
    from pathlib import Path
    path=Path(__file__).resolve().parents[1]/"examples"/"databus"/"parallel-load.mano"
    model,staged=load(path)
    assert tuple(model.registers.values())==(6,6,6)
    assert model.memory.read(9)==6 and model.memory.read(6)==0
    assert len(model.history)==3 and staged==(("RAM",),("R1",),0)
