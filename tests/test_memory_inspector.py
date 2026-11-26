import pytest
from memory_inspector import parse_address, page_addresses, memory_rows


@pytest.mark.parametrize('text,address', [('0', 0), ('fff', 4095), ('0xAbC', 0xABC),
    (' ۱۲f ', 0x12F), ('١٠٠', 0x100), ('000', 0)])
def test_parse(text, address):
    assert parse_address(text) == address


@pytest.mark.parametrize('text', ['', '0x', '1000', '-1', '+1', 'A B', 'G', '０'])
def test_invalid_text(text):
    with pytest.raises(ValueError):
        parse_address(text)


@pytest.mark.parametrize('address', [-1, 4096, True, 1.5])
def test_invalid_page(address):
    with pytest.raises(ValueError):
        page_addresses(address)


@pytest.mark.parametrize('address,start', [(0, 0), (15, 0), (16, 16), (4095, 4080)])
def test_page(address, start):
    assert page_addresses(address) == tuple(range(start, start + 16))


def test_live_read_and_no_accumulation():
    memory = [0] * 4096
    known = {2, 4095}
    memory[0xABC] = 0x1234
    rows = dict(memory_rows(memory, known, 0xABC))
    assert len(rows) == 18 and rows[0xABC] == 0x1234
    memory[0xABC] = 0x5678
    assert dict(memory_rows(memory, known, 0xABC))[0xABC] == 0x5678
    assert 0xABC not in dict(memory_rows(memory, known, 0x100))
    assert known == {2, 4095}
    assert memory_rows(memory, known) == [(2, 0), (4095, 0)]


def test_invalid_memory_shape():
    with pytest.raises(ValueError):
        memory_rows([0], {0})
    with pytest.raises(ValueError):
        memory_rows([0] * 4096, {4096})
