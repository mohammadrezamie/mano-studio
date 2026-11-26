from itertools import product
from pathlib import Path
import pytest
from logic_exercise import KarnaughExercise, StateExercise
from native_exercise import save, load, restore
from state_synthesis import design_state_machine
from boolean_minimizer import minimize
import mano_file

ROOT = Path(__file__).resolve().parents[1] / "examples" / "design"


@pytest.mark.parametrize("form", ["SOP", "POS"])
@pytest.mark.parametrize("bits", [2, 3, 4])
def test_map_native_legacy(tmp_path, bits, form):
    ex = KarnaughExercise(tuple((0, 1, None)[i % 3] for i in range(2**bits)), form)
    for suffix in (".mano", ".mano-exercise.json"):
        path = tmp_path / ("تمرین" + suffix)
        save(path, ex)
        assert load(path, "karnaugh") == ex


@pytest.mark.parametrize("mode", ["Moore", "Mealy"])
@pytest.mark.parametrize("ff", ["D", "T", "JK"])
@pytest.mark.parametrize("bits", [1, 2, 3])
def test_state_native(tmp_path, mode, ff, bits):
    size = 2**bits
    rows = tuple(((q+x)%size, q%2 if mode=="Moore" else x) for q in range(size) for x in (0,1))
    ex = StateExercise(bits, mode, ff, rows)
    path = tmp_path / "machine.mano"
    save(path, ex)
    result = load(path, "state-design")
    assert result == ex
    model = design_state_machine(result.bits, result.table, result.mode, result.flipflop)
    assert tuple(model.step(q,x) for q in range(size) for x in (0,1)) == rows


@pytest.mark.parametrize("payload", [
    {"values":[0,1,0,1],"form":"SOP","kind":"rtl"},
    {"values":[0,1,True,0],"form":"SOP"},
    {"values":[0,1,0,1],"form":"bad"},
    {"values":[0,1,0,1],"form":"SOP","extra":1},
])
def test_invalid(payload):
    with pytest.raises(ValueError):
        restore("karnaugh",payload)


def test_wrong_kind(tmp_path):
    path=tmp_path/"x.mano"
    mano_file.save(path,"rtl","AC ← 0")
    with pytest.raises(ValueError):
        load(path,"karnaugh")
    with pytest.raises(ValueError):
        load(path)


def test_saved_majority():
    ex=load(ROOT/"majority.mano","karnaugh")
    cover=minimize(ex.values,ex.form)
    assert all(cover.evaluate(i)==int(i.bit_count()>=2) for i in range(8))


def test_saved_overlap_detector():
    ex=load(ROOT/"overlap-101.mano","state-design")
    model=design_state_machine(ex.bits,ex.table,ex.mode,ex.flipflop)
    for length in range(9):
        for seq in product((0,1),repeat=length):
            q=0
            for i,x in enumerate(seq):
                q,y=model.step(q,x)
                assert y==int(seq[max(0,i-2):i+1]==(1,0,1))


def test_saved_parity():
    ex=load(ROOT/"parity.mano","state-design")
    model=design_state_machine(ex.bits,ex.table,ex.mode,ex.flipflop)
    for seq in product((0,1),repeat=8):
        q=0
        for i,x in enumerate(seq):
            q,y=model.step(q,x)
            assert y==sum(seq[:i])%2
        assert q==sum(seq)%2
