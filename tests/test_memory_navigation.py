import pytest
from memory_navigation import adjacent_page


@pytest.mark.parametrize('address,direction,expected', [
    (None, 1, 0), (None, -1, None), (0, -1, None), (15, -1, None),
    (0, 1, 16), (15, 1, 16), (16, -1, 0), (31, 1, 32),
    (4079, 1, 4080), (4080, 1, None), (4095, 1, None), (4095, -1, 4064),
])
def test_adjacent(address, direction, expected):
    assert adjacent_page(address, direction) == expected


@pytest.mark.parametrize('direction', [0, 2, -2, True, 1.0, None])
def test_invalid_direction(direction):
    with pytest.raises(ValueError):
        adjacent_page(0, direction)


@pytest.mark.parametrize('address', [-1, 4096, True, 1.0])
def test_invalid_address(address):
    with pytest.raises(ValueError):
        adjacent_page(address, 1)


def test_visit_every_page_both_directions():
    seen = []
    address = adjacent_page(None, 1)
    while address is not None:
        seen.append(address)
        address = adjacent_page(address, 1)
    assert seen == list(range(0, 4096, 16))
    backwards = []
    address = 4095
    while address is not None:
        backwards.append(address & ~15)
        address = adjacent_page(address, -1)
    assert backwards == seen[::-1]
