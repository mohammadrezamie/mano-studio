from simulator import CPU
from assembler import assemble
from execution_history import ExecutionHistory

def test_reverse_store_and_halt():
    p=assemble("LDA 100\nSTA 101\nHLT\nORG 100\nDEC 5\nDEC 9")
    cpu=CPU(p.words,p.entry)
    h=ExecutionHistory(cpu)
    initial=cpu.registers()
    for _ in range(3): h.step()
    assert cpu.halted and cpu.memory[0x101]==5
    h.back()
    assert not cpu.halted
    h.back()
    assert cpu.memory[0x101]==9
    h.back()
    assert cpu.registers()==initial and h.steps==0
    assert h.back() is None

def test_bounded_history_and_barrier():
    cpu=CPU({0:0x4000})
    h=ExecutionHistory(cpu,limit=2)
    for _ in range(4): h.step()
    assert len(h.entries)==2 and h.steps==4
    h.back()
    h.back()
    assert h.steps==2 and h.back() is None
    h.step()
    h.barrier()
    assert not h.entries and h.steps==3

def test_breakpoint_at_next_pc():
    cpu=CPU({0:0x7800,1:0x7001})
    h=ExecutionHistory(cpu)
    assert h.toggle_breakpoint(1)
    assert not h.should_break()
    h.step()
    assert h.should_break()
    assert not h.toggle_breakpoint(1)
    assert not h.should_break()

def test_interrupt_reverse():
    cpu=CPU({0:0xF080,1:0x7001})
    h=ExecutionHistory(cpu)
    h.step()
    before=cpu.registers()
    h.step()
    assert cpu.memory[0]==1
    h.back()
    assert cpu.memory[0]==0xF080 and cpu.registers()==before
