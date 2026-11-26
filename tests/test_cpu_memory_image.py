import pytest
from cpu_memory_image import sparse_memory, expand_sparse


def test_full_image_round_trip():
    memory = [(i * 257) & 65535 for i in range(4096)]
    rows = sparse_memory(memory)
    words = expand_sparse(rows)
    assert [words.get(i, 0) for i in range(4096)] == memory
    assert rows == sorted(rows)


@pytest.mark.parametrize('word', [False, True, 0.0, None, '', -1, 65536])
def test_reject_invalid_words_even_falsy(word):
    memory = [0] * 4096
    memory[-1] = word
    with pytest.raises(ValueError):
        sparse_memory(memory)


@pytest.mark.parametrize('length', [0, 4095, 4097])
def test_reject_invalid_length(length):
    with pytest.raises(ValueError):
        sparse_memory([0] * length)


@pytest.mark.parametrize('rows', [[[0, 0]], [[0, 1], [0, 2]], [[4096, 1]],
                                  [[True, 1]], [[1, False]], [[1, 65536]], [[1]],
                                  [[1, 1, 2]], {}, None])
def test_reject_malformed_sparse(rows):
    with pytest.raises(ValueError):
        expand_sparse(rows)


def test_empty_and_last_address():
    memory = [0] * 4096
    assert sparse_memory(memory) == [] and expand_sparse([]) == {}
    memory[-1] = 65535
    assert sparse_memory(memory) == [[4095, 65535]]
    assert expand_sparse([[4095, 65535]]) == {4095: 65535}
