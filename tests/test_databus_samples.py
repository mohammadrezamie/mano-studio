import json
from pathlib import Path
import pytest
from databus_lab import Databus
from databus_samples import SAMPLES,run_sample


@pytest.mark.parametrize("scenario",SAMPLES,ids=lambda s:s["id"])
def test_saved_experiment(scenario):
    path=Path(__file__).resolve().parents[1]/"examples"/"databus"/(scenario["id"]+".mano-databus.json")
    assert json.loads(path.read_text(encoding="utf-8"))==scenario
    m=Databus()
    m.tick(("EXT",),("AR","R0","RAM"),15)
    run_sample(m,scenario)
    expected=scenario["expected"]
    assert list(m.registers.values())==expected["registers"]
    assert [m.memory.read(a) for a in range(16)]==[dict(expected["memory"]).get(a,0) for a in range(16)]
    assert len(m.history)==len(scenario["steps"])
    if "bus" in expected:
        assert m.history[-1].bus==expected["bus"]
    if "flags" in expected:
        r=m.history[-1].arithmetic
        assert [r.carry,r.overflow,r.negative,r.zero]==expected["flags"]
