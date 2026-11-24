from example_catalog import EXAMPLES, computer_source
from rtl_translator import translate
from assembler import assemble
from simulator import CPU


def test_examples_translate_and_execute():
    expected = {"addition":8, "registers":0xFFFE, "indirect":42, "conditional":0}
    for example in EXAMPLES:
        result=translate(example.rtl)
        assert result.ok
        program=assemble(computer_source(example,result.assembly))
        assert program.ok
        cpu=CPU(program.words,program.entry)
        for _ in range(20):
            if cpu.halted:
                break
            cpu.step()
        assert cpu.halted and cpu.ac==expected[example.key]
        if example.key=="addition":
            assert cpu.memory[0x102]==8
        if example.key=="indirect":
            assert cpu.memory[0x101]==42
