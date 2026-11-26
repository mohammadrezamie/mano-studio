"""Canonical sparse 4096-word images for CPU checkpoints."""


def integer(value, maximum):
    return type(value) is int and 0 <= value <= maximum


def sparse_memory(memory):
    if not isinstance(memory, (list, tuple)) or len(memory) != 4096:
        raise ValueError('Expected exactly 4096 memory words')
    if any(not integer(word, 65535) for word in memory):
        raise ValueError('Invalid 16-bit memory word')
    return [[address, word] for address, word in enumerate(memory) if word != 0]


def expand_sparse(rows):
    if not isinstance(rows, list) or len(rows) > 4096:
        raise ValueError('Invalid CPU memory')
    words = {}
    for row in rows:
        if (not isinstance(row, list) or len(row) != 2 or not integer(row[0], 4095)
                or not integer(row[1], 65535) or row[1] == 0 or row[0] in words):
            raise ValueError('Invalid or duplicate sparse memory word')
        words[row[0]] = row[1]
    return words
