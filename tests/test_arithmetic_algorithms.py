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


from arithmetic_algorithms import nonrestoring_division, signed_division


@pytest.mark.parametrize("width", [4, 8])
def test_nonrestoring_exhaustive(width):
    limit = 1 << width
    for a in range(limit):
        for b in range(1, limit):
            out = nonrestoring_division(a, b, width)
            assert (out.quotient, out.remainder) == divmod(a, b)
            assert len(out.steps) == width
            r, q = 0, a
            for i, row in enumerate(out.steps, 1):
                assert row.cycle == i
                assert row.shifted_remainder == 2*r + (q >> (width-1))
                assert row.operation == ("-B" if r >= 0 else "+B")
                assert row.partial_remainder == row.shifted_remainder + (-b if r >= 0 else b)
                assert -b <= row.partial_remainder < b
                assert row.quotient == ((q << 1) % limit) + int(row.partial_remainder >= 0)
                r, q = row.partial_remainder, row.quotient
            assert out.correction == (b if r < 0 else 0)
            assert out.remainder == r + out.correction


@pytest.mark.parametrize("width", [4, 8])
def test_signed_division_exhaustive(width):
    bound = 1 << (width-1)
    mask = 2*bound-1
    for a in range(-bound, bound):
        for b in range(-bound, bound):
            if b == 0:
                continue
            out = signed_division(a & mask, b & mask, width)
            expected = abs(a)//abs(b)
            if (a < 0) != (b < 0):
                expected = -expected
            assert out.quotient == expected
            assert out.remainder == a - b*expected
            assert abs(out.remainder) < abs(b)
            assert out.remainder == 0 or (out.remainder < 0) == (a < 0)
            assert out.overflow == (a == -bound and b == -1)
            assert out.steps[-1].quotient == abs(expected)
            assert out.steps[-1].remainder == abs(out.remainder)


@pytest.mark.parametrize("width", [12, 16])
def test_division_boundaries(width):
    limit = 1 << width
    for a,b in [(0,1),(limit-1,1),(limit-1,limit-1),(1,limit-1),(limit//2,3)]:
        r = nonrestoring_division(a,b,width)
        assert (r.quotient,r.remainder)==divmod(a,b)
    assert signed_division(limit//2,limit-1,width).overflow
    assert signed_division(limit//2,1,width).quotient == -limit//2


@pytest.mark.parametrize("fn,args", [(nonrestoring_division,(1,0,4)),
    (nonrestoring_division,(16,1,4)), (signed_division,(1,0,4)),
    (signed_division,(-1,1,4))])
def test_new_division_invalid(fn,args):
    with pytest.raises(ValueError):
        fn(*args)
