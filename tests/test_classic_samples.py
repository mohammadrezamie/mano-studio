from pathlib import Path
import pytest
from classic_samples import SAMPLES, load_sample
from circuit_composition import compose
from circuit_document import CircuitDocument
from logic_engine import CIRCUITS


@pytest.mark.parametrize("sample",SAMPLES,ids=lambda s:s["id"])
def test_saved_sample_matches_catalog_and_oracle(sample):
    doc=load_sample(sample["id"])
    path=Path(__file__).resolve().parents[1]/"examples"/"circuits"/(sample["id"]+".mano-logic.json")
    assert CircuitDocument.loads(path.read_text(encoding="utf-8"))==doc
    for bits,out in doc.compile().truth_table():
        if sample["id"]=="full-adder-halves":
            assert out==(sum(bits)%2,sum(bits)//2)
        elif sample["id"]=="nand-xor":
            assert out==(bits[0]^bits[1],)
        elif sample["id"]=="mux-majority":
            assert out==(int(sum(bits)>=2),)
        elif sample["id"]=="decoder-enabled-low":
            a1,a0,en=bits
            assert out==tuple(int(not (en and k==2*a1+a0)) for k in range(4))
        elif sample["id"]=="comparator-two-bit":
            a1,a0,b1,b0=bits
            a,b=2*a1+a0,2*b1+b0
            assert out==(int(a<b),int(a==b),int(a>b))
        elif sample["id"]=="adder-subtractor-two-bit":
            a1,a0,b1,b0,m=bits
            a,b=2*a1+a0,2*b1+b0
            expected=(a-b if m else a+b)%4
            assert out==(expected>>1,expected&1,int(a>=b) if m else int(a+b>=4))
        else:
            pytest.fail("Missing sample oracle")


def test_compose_actual_documents():
    half=CircuitDocument.from_circuit(CIRCUITS["half_adder"])
    or_gate=CircuitDocument.from_circuit(CIRCUITS["or"])
    second=compose(half,half,"h2",{"A":"sum","B":None})
    result=compose(second,or_gate,"or1",{"A":"carry","B":"h2_carry"})
    assert CircuitDocument.loads(result.dumps())==result
    for bits,out in result.compile().truth_table():
        values=dict(zip((n for n,_ in result.outputs),out))
        assert values["h2_S"]+2*values["or1_Y"]==sum(bits)
    assert half==CircuitDocument.from_circuit(CIRCUITS["half_adder"])
    with pytest.raises(ValueError):
        compose(second,half,"h2",{"A":"sum","B":None})
