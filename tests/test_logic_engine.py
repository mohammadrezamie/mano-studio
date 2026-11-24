from itertools import product
import pytest
from logic_engine import CIRCUITS, Circuit, Gate, gate_value, ripple_adder


@pytest.mark.parametrize("a,b", product((0,1),repeat=2))
def test_basic_gates(a,b):
    expected={"AND":a&b,"OR":a|b,"XOR":a^b,"NAND":1-(a&b),
              "NOR":1-(a|b),"XNOR":1-(a^b)}
    for op,value in expected.items():
        assert gate_value(op,a,b)==value
    assert gate_value("NOT",a)==1-a


def test_half_adder():
    for bits,out in CIRCUITS["half_adder"].truth_table():
        assert out[0]+2*out[1]==sum(bits)


def test_full_adder():
    for bits,out in CIRCUITS["full_adder"].truth_table():
        assert out[0]+2*out[1]==sum(bits)


def test_decoder():
    for bits,out in CIRCUITS["decoder"].truth_table():
        assert sum(out)==1 and out[2*bits[0]+bits[1]]==1


def test_encoder_validity():
    for bits,out in CIRCUITS["encoder"].truth_table():
        assert out[2]==int(sum(bits)==1)
        if out[2]:
            assert 2*out[0]+out[1]==bits.index(1)


def test_mux_demux():
    for (a,b,s),(y,) in CIRCUITS["mux"].truth_table():
        assert y==(b if s else a)
    for (d,s),(y0,y1) in CIRCUITS["demux"].truth_table():
        assert (y0,y1)==((0,d) if s else (d,0))


def test_subtraction():
    for (a,b),(d,borrow) in CIRCUITS["half_subtractor"].truth_table():
        assert d-2*borrow==a-b


def test_all_4_bit_additions():
    for bits,out in CIRCUITS["ripple4"].truth_table():
        a=sum(v<<i for i,v in enumerate(bits[:4]))
        b=sum(v<<i for i,v in enumerate(bits[4:8]))
        assert sum(v<<i for i,v in enumerate(out))==a+b+bits[8]


def test_invalid_netlist_and_input():
    with pytest.raises(ValueError):
        Circuit(("A",),(Gate("Y","NOT",("Y",)),),(("Y","Y"),),("",""),("",""))
    with pytest.raises(ValueError):
        CIRCUITS["half_adder"].evaluate({"A":2,"B":0})
    with pytest.raises(ValueError):
        list(ripple_adder(8).truth_table())


def test_catalog_complete():
    assert len(CIRCUITS)==15
    for circuit in CIRCUITS.values():
        assert len(list(circuit.truth_table()))==2**len(circuit.inputs)
