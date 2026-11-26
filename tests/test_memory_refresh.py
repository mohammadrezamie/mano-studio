import pytest
from memory_refresh import refresh_plan, row_for_address


@pytest.mark.parametrize('old,new,expected', [
    ([], [], (False, ())),
    ([], [(0, 0)], (True, (0,))),
    ([(0, 0)], [], (True, ())),
    ([(0, 0)], [(0, 0)], (False, ())),
    ([(0, 0)], [(0, 1)], (False, (0,))),
    ([(0, 0)], [(1, 0)], (True, (0,))),
    ([(0, 0), (2, 0)], [(0, 0), (1, 0), (2, 0)], (True, (0, 1, 2))),
])
def test_refresh_plan(old, new, expected):
    assert refresh_plan(old, new) == expected


def test_full_memory_single_word_change():
    old = [(i, 0) for i in range(4096)]
    new = old.copy()
    new[4095] = (4095, 65535)
    assert refresh_plan(old, new) == (False, (4095,))
    assert refresh_plan(new, new) == (False, ())
    assert old[-1] == (4095, 0)


@pytest.mark.parametrize('address,expected', [(0, 0), (5, 1), (4095, 2), (7, None), (None, None)])
def test_selection(address, expected):
    assert row_for_address([(0, 1), (5, 8), (4095, 0)], address) == expected
