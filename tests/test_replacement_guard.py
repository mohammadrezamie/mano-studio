import pytest
from replacement_guard import allow_replace


@pytest.mark.parametrize('dirty,has_document,answer,expected,calls', [
    (True, True, True, True, ['dirty']),
    (True, True, False, False, ['dirty']),
    (True, False, False, False, ['dirty']),
    (True, False, True, True, ['dirty']),
    (False, True, True, True, ['clean']),
    (False, True, False, False, ['clean']),
    (False, False, False, True, []),
])
def test_replacement_policy(dirty, has_document, answer, expected, calls):
    seen = []
    def confirm_dirty():
        seen.append('dirty')
        return answer
    def confirm_clean():
        seen.append('clean')
        return answer
    assert allow_replace(dirty, has_document, confirm_dirty, confirm_clean) is expected
    assert seen == calls


def test_failed_save_exception_is_not_swallowed():
    def fail():
        raise OSError('disk unavailable')
    with pytest.raises(OSError):
        allow_replace(True, True, fail, lambda: True)
