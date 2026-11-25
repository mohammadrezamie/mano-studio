from itertools import product
import pytest
from boolean_laws import LAWS, BY_ID, compare


@pytest.mark.parametrize('law', LAWS, ids=lambda law: law.id)
@pytest.mark.parametrize('dual', [False, True])
def test_law(law, dual):
    left, right, rows = compare(law.id, dual)
    assert len(rows) == 8
    assert [r[:3] for r in rows] == list(product((0, 1), repeat=3))
    assert all(a == b for *_, a, b in rows)
    assert left.dual().dual() == left and right.dual().dual() == right
    for a, b, c, x, y in rows:
        env = dict(zip('ABC', (1-a, 1-b, 1-c)))
        assert left.dual().evaluate(env) == 1-x
        assert right.dual().evaluate(env) == 1-y


def test_known_independent_outputs():
    assert len(BY_ID) == len(LAWS) == 12
    for dual in (False, True):
        _, _, rows = compare('de-morgan', dual)
        for a, b, c, lhs, rhs in rows:
            assert lhs == rhs == (1-(a&b) if dual else 1-(a|b))
        _, _, rows = compare('consensus', dual)
        for a, b, c, lhs, rhs in rows:
            expected = ((a|b)&((1-a)|c)) if dual else ((a&b)|((1-a)&c))
            assert lhs == rhs == expected
    assert str(compare('identity')[0]) == '(A + 0)'
    assert str(compare('identity', True)[0]) == '(A · 1)'


@pytest.mark.parametrize('law_id,dual', [('unknown',False),('identity',1)])
def test_invalid(law_id,dual):
    with pytest.raises(ValueError):
        compare(law_id,dual)
