import pytest
from cpu_organization import MemoryStack,resolve_address


def test_memory_stack_bounds_and_retained_words():
    s=MemoryStack(100,102)
    assert s.empty and s.sp==103
    for i in range(3):
        e=s.push(i+8)
        assert e.address==102-i and s.occupied(e.address)
    assert s.full and s.sp==100
    snapshot=dict(s.words)
    with pytest.raises(ValueError):s.push(10)
    assert s.words==snapshot and s.sp==100
    for value in (10,9,8):assert s.pop().value==value
    assert s.empty and s.words==snapshot
    with pytest.raises(ValueError):s.pop()
    assert s.sp==103


@pytest.mark.parametrize("mode,field,reg,pc,ea,operand,after,reads",[
    ("implied",0,0,0,None,None,0,()),
    ("immediate",0x100,0,0,None,0x100,0,()),
    ("register",0,0x100,0,None,0x100,0x100,()),
    ("register_indirect",0,0x100,0,0x100,0x200,0x100,((0x100,0x200),)),
    ("auto_increment",0,65535,0,65535,9,0,((65535,9),)),
    ("auto_decrement",0,0,0,65535,9,65535,((65535,9),)),
    ("direct",0x100,0,0,0x100,0x200,0,((0x100,0x200),)),
    ("indirect",0x100,0,0,0x200,0xABCD,0,((0x100,0x200),(0x200,0xABCD))),
    ("relative",0xFFFF,0,0,65535,9,0,((65535,9),)),
    ("indexed",1,65535,0,0,0,65535,((0,0),)),
    ("base",0xFFFE,0x202,0,0x200,0xABCD,0x202,((0x200,0xABCD),))])
def test_address_modes(mode,field,reg,pc,ea,operand,after,reads):
    memory={0x100:0x200,0x200:0xABCD,65535:9}
    initial=dict(memory)
    r=resolve_address(mode,field,reg,pc,memory)
    assert (r.effective_address,r.operand,r.register_after,r.reads)==(ea,operand,after,reads)
    assert memory==initial


@pytest.mark.parametrize("mode",["relative","indexed","base"])
def test_all_displacements(mode):
    for field in range(65536):
        r=resolve_address(mode,field,0xFFFE,0xFFFE,{})
        assert r.effective_address==(0xFFFE+field)%65536


def test_invalid_address_inputs():
    with pytest.raises(ValueError):resolve_address("missing",0,0,0,{})
    with pytest.raises(ValueError):resolve_address("direct",65536,0,0,{})
    with pytest.raises(ValueError):resolve_address("indirect",0,0,0,{0:65536})
