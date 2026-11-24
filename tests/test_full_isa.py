import pytest
from rtl_translator import translate
from instruction_catalog import TEMPLATES, build_rtl

MEMORY = "AND ADD LDA STA BUN BSA ISZ".split()
FIXED = "CLA CLE CMA CME CIR CIL INC SPA SNA SZA SZE HLT INP OUT SKI SKO ION IOF".split()


def test_catalog_complete():
    assert set(TEMPLATES) == set(MEMORY + FIXED)


@pytest.mark.parametrize("mnemonic", MEMORY)
@pytest.mark.parametrize("indirect", [False, True])
def test_memory(mnemonic, indirect):
    result = translate(build_rtl(mnemonic, "1a", indirect))
    assert result.assembly == mnemonic + " 01A" + (" I" if indirect else "")


@pytest.mark.parametrize("mnemonic", FIXED)
def test_fixed(mnemonic):
    assert translate(build_rtl(mnemonic)).assembly == mnemonic


@pytest.mark.parametrize("rtl", ["M[100] = PC, PC = 101 + 1", "M[100] = M[101] + 1, IF M[100] = 0 THEN PC = PC + 1", "AC = M[M[1000]]", "IF AC[15] = 2 THEN PC = PC + 1"])
def test_invalid_compound(rtl):
    assert not translate(rtl).ok


@pytest.mark.parametrize("address", ["", "1000", "GG", "1 0"])
def test_builder_invalid(address):
    with pytest.raises(ValueError):
        build_rtl("LDA", address)
