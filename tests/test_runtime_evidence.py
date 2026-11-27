import io
import zipfile
import pytest
from installer.runtime_evidence import scan


def run(payload, runtime=(3, 5, 10)):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        for name, data in payload.items():
            z.writestr(name, data)
    with zipfile.ZipFile(buffer) as z:
        return scan(z, '3.14.10', runtime)


@pytest.mark.parametrize('version', [b'3.0.16', b'3.5.8', b'3.6.0'])
def test_unapproved_series_or_patch(version):
    result = run({'ManoStudio/libcrypto-3.dll': b'OpenSSL ' + version})
    assert result['flags'][0]['code'] == 'crypto-version-review'


def test_current_baseline_is_not_release_approval():
    result = run({'ManoStudio/libcrypto-3.dll': b'OpenSSL 3.5.10',
                  'ManoStudio/libssl-3.dll': b'no version string'})
    assert not result['flags']
    assert result['build_ssl_version'] == [3, 5, 9]
    assert result['public_release_approved'] is False
    assert result['manual_review_required'] is True


def test_unknown_crypto_and_runtime():
    result = run({'ManoStudio/libcrypto-3.dll': b'unknown'}, (3, 0, 16))
    assert {x['code'] for x in result['flags']} == {'unknown-crypto-version', 'build-ssl-version-review'}


def test_missing_crypto():
    assert run({})['flags'] == [{'code': 'missing-crypto-evidence'}]


def test_multiple_embedded_versions_require_review():
    result = run({'ManoStudio/libcrypto-3.dll': b'OpenSSL 3.5.10\0OpenSSL 3.5.11'})
    assert result['flags'] == [{'code': 'unknown-crypto-version', 'path': 'ManoStudio/libcrypto-3.dll'}]


def test_openssl_three_tuple_uses_fourth_patch_component():
    result = run({'libcrypto-3.dll': b'OpenSSL 3.5.9'}, (3, 5, 0, 9, 0))
    assert result['build_ssl_version'] == [3, 5, 9]
    assert result['flags'] == []
