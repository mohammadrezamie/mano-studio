import zipfile
import pytest
from regression_evidence import compare, load_report


def archive(path, cases, *, tests=1, failures=0, errors=0, skipped=0):
    xml = (f'<testsuites><testsuite tests="{tests}" failures="{failures}" errors="{errors}" skipped="{skipped}">'
           f'{cases}</testsuite></testsuites>')
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('regression.xml', xml)
    return path


GOOD = '<testcase classname="tests.workspace" name="test_one" time="1.5"/>'


def test_exact_success(tmp_path):
    a = archive(tmp_path / 'a.zip', GOOD)
    b = archive(tmp_path / 'b.zip', GOOD)
    report = compare(a, b)
    assert report['same_test_identities'] and report['regression_evidence_clean']
    assert report['public_release_approved'] is False
    assert report['windows']['slowest_modules'][0]['percent'] == 100


def test_identity_mismatch(tmp_path):
    a = archive(tmp_path / 'a.zip', GOOD)
    b = archive(tmp_path / 'b.zip', GOOD.replace('test_one', 'test_two'))
    report = compare(a, b)
    assert not report['regression_evidence_clean']
    assert report['windows_only'] == report['ubuntu_only'] == 1


@pytest.mark.parametrize('tag,counts', [('failure', {'failures': 1}), ('error', {'errors': 1}), ('skipped', {'skipped': 1})])
def test_nonpassing_result(tmp_path, tag, counts):
    a = archive(tmp_path / 'a.zip', GOOD[:-2] + f'><{tag}/></testcase>', **counts)
    b = archive(tmp_path / 'b.zip', GOOD)
    assert not compare(a, b)['regression_evidence_clean']


@pytest.mark.parametrize('cases,tests', [(GOOD + GOOD, 2), (GOOD, 2), (GOOD.replace('1.5', 'nan'), 1)])
def test_invalid_reports(tmp_path, cases, tests):
    with pytest.raises(ValueError):
        load_report(archive(tmp_path / 'bad.zip', cases, tests=tests))
