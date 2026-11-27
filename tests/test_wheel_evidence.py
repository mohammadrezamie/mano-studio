import pytest
from installer.wheel_evidence import validate, REQUIRED, pins


def report():
    expected = {name: '1.2.3' for name in REQUIRED}
    rows = [{'metadata': {'name': name, 'version': version},
             'download_info': {'url': 'https://files.pythonhosted.org/packages/' + name + '.whl',
                               'archive_info': {'hashes': {'sha256': 'a' * 64}}}}
            for name, version in sorted(expected.items())]
    return {'version': '1', 'install': rows}, expected


def test_report_records_evidence_not_approval():
    value, expected = report()
    result = validate(value, expected)
    assert set(result['packages']) == REQUIRED
    assert result['independent_authenticity_verified'] is False
    assert result['redistribution_approved'] is False


@pytest.mark.parametrize('defect', ['version', 'url', 'credentials', 'query', 'sdist', 'hash', 'missing', 'duplicate', 'unpinned'])
def test_report_rejects_bad_evidence(defect):
    value, expected = report()
    row = value['install'][0]
    download = row['download_info']
    if defect == 'version':
        row['metadata']['version'] = '2.0'
    elif defect == 'url':
        download['url'] = 'https://files.pythonhosted.org.example.com/qt.whl'
    elif defect == 'credentials':
        download['url'] = 'https://token@files.pythonhosted.org/qt.whl'
    elif defect == 'query':
        download['url'] += '?secret=hidden'
    elif defect == 'sdist':
        download['url'] = 'https://files.pythonhosted.org/qt.tar.gz'
    elif defect == 'hash':
        download['archive_info']['hashes'] = {}
    elif defect == 'missing':
        value['install'].pop(0)
    elif defect == 'duplicate':
        value['install'].append(row)
    elif defect == 'unpinned':
        row['metadata']['name'] = 'Unknown'
    with pytest.raises(ValueError):
        validate(value, expected)


def test_constraints(tmp_path):
    path = tmp_path / 'constraints.txt'
    path.write_text('# pinned\nPySide6_Essentials==6.12.0\n')
    assert pins(path) == {'pyside6-essentials': '6.12.0'}
    path.write_text('A_B==1\na-b==2\n')
    with pytest.raises(ValueError):
        pins(path)
