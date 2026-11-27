"""Offline installer preflight contracts; no execution, real signing, or network."""
import hashlib
import pytest
from update_download import Asset
from installer_trust import SignatureEvidence, verify_installer

PIN = "a"*64

def candidate(tmp_path, tag="v1.0.1"):
    name = "ManoStudio-Setup-"+tag+"-x64.exe"
    path = tmp_path/name
    path.write_bytes(b"fixture, not an executable")
    asset = Asset("https://github.com/mohammadrezamie/mano-studio/releases/download/"+tag+"/"+name,
                  name, path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest())
    return path,asset

def verify(path, asset, **kw):
    options = dict(tag="v1.0.1", current="1.0.0", prerelease=False,
                   trusted_signers={PIN}, signature_reader=lambda _:SignatureEvidence("Valid",PIN))
    options.update(kw)
    return verify_installer(path,asset,**options)

def test_valid_contract(tmp_path):
    p,a=candidate(tmp_path)
    assert verify(p,a).certificate_sha256 == PIN

def test_no_trust_is_fail_closed(tmp_path):
    p,a=candidate(tmp_path)
    with pytest.raises(ValueError,match="not provisioned"):
        verify(p,a,trusted_signers=set(),signature_reader=lambda _:pytest.fail("signature"))

@pytest.mark.parametrize("status,signer",[("NotSigned",PIN),("HashMismatch",PIN),("Valid","b"*64)])
def test_signature_rejection(tmp_path,status,signer):
    p,a=candidate(tmp_path)
    with pytest.raises(ValueError):
        verify(p,a,signature_reader=lambda _:SignatureEvidence(status,signer))

def test_modified_file(tmp_path):
    p,a=candidate(tmp_path)
    p.write_bytes(b"x"*a.size)
    with pytest.raises(ValueError,match="digest"):
        verify(p,a)

def test_changed_during_signature(tmp_path):
    p,a=candidate(tmp_path)
    def reader(path):
        path.write_bytes(b"x"*a.size)
        return SignatureEvidence("Valid",PIN)
    with pytest.raises(ValueError):
        verify(p,a,signature_reader=reader)

@pytest.mark.parametrize("current,pre",[("1.0.1",False),("1.1.0-beta.1",False),("1.0.0",True)])
def test_wrong_channel_or_not_newer(tmp_path,current,pre):
    p,a=candidate(tmp_path)
    with pytest.raises(ValueError,match="channel/version"):
        verify(p,a,current=current,prerelease=pre)

def test_beta_channel(tmp_path):
    p,a=candidate(tmp_path,"v1.1.0-beta.2")
    assert verify(p,a,tag="v1.1.0-beta.2",current="1.1.0-beta.1",prerelease=True)
