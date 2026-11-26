from itertools import product
import pytest
from storage_elements import Storage, PINS, step


@pytest.mark.parametrize("kind", ["SR_NOR", "SR_NAND"])
def test_sr_truth_tables(kind):
    for q in (0,1):
        initial=Storage(q,1-q)
        expected = ((initial,Storage(0,1),Storage(1,0),Storage(0,0))
                    if kind=="SR_NOR" else
                    (Storage(1,1),Storage(1,0),Storage(0,1),initial))
        for bits,wanted in zip(product((0,1),repeat=2),expected):
            assert step(kind,initial,dict(zip(PINS[kind],bits)))==wanted


@pytest.mark.parametrize("kind,forbidden,inactive,set_inputs,forbidden_output", [
    ("SR_NOR",(1,1),(0,0),(1,0),Storage(0,0)),
    ("SR_NAND",(0,0),(1,1),(0,1),Storage(1,1)),
])
def test_forbidden_release_and_recovery(kind,forbidden,inactive,set_inputs,forbidden_output):
    apply=lambda state,bits:step(kind,state,dict(zip(PINS[kind],bits)))
    invalid=apply(Storage(),forbidden)
    assert invalid==forbidden_output and not invalid.known
    unknown=apply(invalid,inactive)
    assert unknown==Storage(None,None) and not unknown.known
    assert apply(unknown,inactive)==unknown
    assert apply(unknown,set_inputs)==Storage(1,0)


def test_d_latch_transparent_and_held():
    for q,d,en in product((0,1),repeat=3):
        expected=d if en else q
        assert step("D_LATCH",Storage(q,1-q),{"D":d,"EN":en})==Storage(expected,1-expected)
    unknown=Storage(None,None)
    assert step("D_LATCH",unknown,{"D":1,"EN":0})==unknown
    assert step("D_LATCH",unknown,{"D":1,"EN":1})==Storage(1,0)


def test_async_dff_exhaustive():
    for q in (0,1,None):
        state=Storage(q,None if q is None else 1-q)
        for d,clk,pre,clr,previous in product((0,1),repeat=5):
            if (pre,clr)==(0,0): expected=None
            elif not pre: expected=1
            elif not clr: expected=0
            elif (previous,clk)==(0,1): expected=d
            else: expected=q
            result=step("D_ASYNC",state,dict(zip(PINS["D_ASYNC"],(d,clk,pre,clr))),previous)
            assert result==Storage(expected,None if expected is None else 1-expected)


@pytest.mark.parametrize("kind,state,pins,clk", [
    ("unknown",Storage(),{},0),
    ("D_LATCH",Storage(),{"D":0},0),
    ("D_LATCH",Storage(),{"D":2,"EN":0},0),
    ("D_LATCH",Storage(),{"D":True,"EN":0},0),
    ("D_LATCH",Storage(3,0),{"D":0,"EN":0},0),
    ("D_ASYNC",Storage(),dict(zip(PINS["D_ASYNC"],(0,0,1,1))),2),
])
def test_invalid(kind,state,pins,clk):
    with pytest.raises(ValueError):
        step(kind,state,pins,clk)
