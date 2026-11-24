import pytest
from arithmetic_algorithms import booth, restoring_division


@pytest.mark.parametrize("width", [4, 8])
def test_booth_exhaustive(width):
    limit = 1 << width
    def signed(x):
        return x if x < limit // 2 else x - limit
    for m in range(limit):
        for q in range(limit):
            product, rows = booth(m, q, width)
            assert product == signed(m) * signed(q)
            assert len(rows) == width
            a, b, prev = 0, q, 0
            for i, row in enumerate(rows, 1):
                assert row.cycle == i
                assert row.pair == f"{b & 1}{prev}"
                expected = a + signed(m) * (prev - (b & 1))
                assert row.accumulator_after_operation == expected
                assert row.accumulator == expected // 2
                assert row.multiplier == (b >> 1) | ((expected & 1) << (width - 1))
                assert row.previous_bit == b & 1
                a, b, prev = row.accumulator, row.multiplier, row.previous_bit


@pytest.mark.parametrize("width", [4, 8])
def test_restoring_exhaustive(width):
    limit = 1 << width
    for dividend in range(limit):
        for divisor in range(1, limit):
            q, r, rows = restoring_division(dividend, divisor, width)
            assert (q, r) == divmod(dividend, divisor)
            assert len(rows) == width
            old_r, old_q = 0, dividend
            for i, row in enumerate(rows, 1):
                assert row.cycle == i
                assert row.shifted_remainder == 2 * old_r + (old_q >> (width - 1))
                assert row.trial_remainder == row.shifted_remainder - divisor
                assert row.restored == (row.trial_remainder < 0)
                assert row.remainder == row.trial_remainder + (divisor if row.restored else 0)
                assert 0 <= row.remainder < divisor
                assert row.quotient == ((old_q << 1) % limit) + int(not row.restored)
                old_r, old_q = row.remainder, row.quotient


@pytest.mark.parametrize("width", [12, 16])
def test_large_boundaries(width):
    limit = 1 << width
    assert booth(limit // 2, limit // 2, width)[0] == (limit // 2) ** 2
    assert booth(limit // 2, 1, width)[0] == -limit // 2
    assert booth(limit // 2, limit - 1, width)[0] == limit // 2
    assert restoring_division(limit - 1, limit - 2, width)[:2] == (1, 1)
    assert restoring_division(0, limit - 1, width)[:2] == (0, 0)


@pytest.mark.parametrize("fn,args", [(booth, (16,1,4)), (booth,(1,-1,4)),
    (restoring_division,(1,0,4)), (restoring_division,(-1,1,4)),
    (restoring_division,(1,16,4)), (booth,(1,1,5))])
def test_invalid(fn,args):
    with pytest.raises(ValueError):
        fn(*args)
