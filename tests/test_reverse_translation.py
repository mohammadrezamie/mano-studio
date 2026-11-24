import pytest
from asm_to_rtl import reverse_translate
from instruction_catalog import TEMPLATES,build_rtl
from rtl_translator import translate

@pytest.mark.parametrize("mnemonic",list(TEMPLATES))
def test_canonical_roundtrip(mnemonic):
    memory="{a}" in TEMPLATES[mnemonic]
    for indirect in ((False,True) if memory else (False,)):
        rtl=build_rtl(mnemonic,"ABC" if memory else "",indirect)
        result=reverse_translate(translate(rtl).assembly)
        assert result.ok and result.rtl==rtl+"\n"

@pytest.mark.parametrize("text",["ORG 100\nHLT","LABEL, CLA","DEC 3","LDA 1000","HLT 1","LDA ZZZ","ADD 100 X","END","", "CLA\nHEX 1"])
def test_no_lossy_or_partial_import(text):
    result=reverse_translate(text)
    assert not result.ok and not result.rtl

def test_case_comments_and_line_error():
    result=reverse_translate(" ; comment\nlda a i # comment\nhlt / stop")
    assert result.ok and translate(result.rtl).assembly=="LDA 00A I\nHLT"
    result=reverse_translate("CLA\n\nBUN FFFF")
    assert not result.ok and result.errors[0].line==3
