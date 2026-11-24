import pytest
from memory_organization import MemoryArray
from memory_interleaving import Interleaving,Request,parse_requests


@pytest.mark.parametrize("banks",[1,2,4])
@pytest.mark.parametrize("interleaved",[True,False])
def test_bijective_mapping_and_actual_chips(banks,interleaved):
    a=MemoryArray(4,8,banks,2,interleaved=interleaved)
    pairs=set()
    for address in range(a.size):
        sel=a.decode(address)
        expected=(address%banks,address//banks) if interleaved else divmod(address,16)
        assert (sel.bank,sel.local)==expected
        assert sel.cs_n[sel.bank]==0 and sum(sel.cs_n)==banks-1
        pairs.add(expected)
        a.write(address,address*257)
    assert len(pairs)==a.size
    assert [a.read(i) for i in range(a.size)]==[i*257 for i in range(a.size)]


@pytest.mark.parametrize("banks",[1,2,4])
@pytest.mark.parametrize("latency",[1,2,4,7])
def test_sequential_interleaving_timing(banks,latency):
    m=Interleaving([Request(i) for i in range(16)],banks,latency)
    rows=m.run()
    expected_starts=[i//banks*max(banks,latency)+i%banks+1 for i in range(16)]
    assert [r.issued.start for r in rows if r.issued]==expected_starts
    assert m.cycles==expected_starts[-1]+latency-1
    assert m.stalls==expected_starts[-1]-16


def test_stride_conflict_and_high_order():
    for addresses,low in [([i*4 for i in range(16)],True),(range(16),False)]:
        m=Interleaving([Request(i) for i in addresses],4,4,low)
        m.run()
        assert m.cycles==64 and m.stalls==45


def test_read_write_same_bank_and_completion():
    m=Interleaving(parse_requests("00:1234 01:ABCD 00 01"),4,4)
    rows=m.run()
    assert [r.value for r in m.results]==[0x1234,0xABCD,0x1234,0xABCD]
    assert m.array.read(0)==0x1234 and m.array.read(1)==0xABCD
    assert m.stalls==2 and m.cycles==9
    assert rows[0].completed==() and rows[3].completed[0].value==0x1234


@pytest.mark.parametrize("text",["","GG","00:10000","00::1"])
def test_invalid_text(text):
    with pytest.raises(ValueError):parse_requests(text)


def test_out_of_bounds():
    with pytest.raises(ValueError):Interleaving([Request(64)],4)
