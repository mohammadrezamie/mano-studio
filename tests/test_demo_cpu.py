from demo_cpu import DemoCPU


def test_addition_demo():
    cpu = DemoCPU()
    assert cpu.step() and (cpu.ac, cpu.pc, cpu.ir) == (5, 1, 0x2100)
    assert cpu.step() and (cpu.ac, cpu.pc, cpu.e) == (8, 2, 0)
    assert cpu.step() and cpu.memory[0x102] == 8
    assert cpu.step() and cpu.halted and cpu.pc == 4
    assert not cpu.step()


def test_demo_carry():
    cpu = DemoCPU()
    cpu.memory[0x100] = 65535
    cpu.memory[0x101] = 1
    cpu.step()
    cpu.step()
    assert (cpu.ac, cpu.e) == (0, 1)
