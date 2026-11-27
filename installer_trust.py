"""Fail-closed installer preflight. This module never launches an executable."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from release_channel import eligible_release
from update_download import Asset, asset_from_release

# Provision reviewed publisher certificate SHA-256 pins before enabling installation.
# Do not populate these from downloaded release metadata or user-editable settings.
TRUSTED_SIGNERS = frozenset()

@dataclass(frozen=True)
class SignatureEvidence:
    status: str
    certificate_sha256: str

def windows_signature(path):
    if sys.platform != "win32":
        raise ValueError("Authenticode validation requires Windows")
    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    if not system_root.is_absolute():
        raise ValueError("Invalid Windows system root")
    executable = system_root / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    script = """
$ErrorActionPreference = 'Stop'
$s = Get-AuthenticodeSignature -LiteralPath $env:MANO_VERIFY_PATH
$hash = ''
if ($null -ne $s.SignerCertificate) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { $hash = ([BitConverter]::ToString($sha.ComputeHash($s.SignerCertificate.RawData))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}
@{status = [string]$s.Status; certificate_sha256 = $hash} | ConvertTo-Json -Compress
"""
    env = dict(os.environ, MANO_VERIFY_PATH=str(path))
    result = subprocess.run([str(executable), "-NoProfile", "-NonInteractive", "-Command", script],
                            env=env, capture_output=True, text=True, timeout=30,
                            check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    data = json.loads(result.stdout)
    return SignatureEvidence(data["status"], data["certificate_sha256"])

def _identity(path, asset):
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or getattr(st, "st_file_attributes", 0) & 0x400:
        raise ValueError("Installer must be a regular non-reparse file")
    if st.st_size != asset.size:
        raise ValueError("Installer length mismatch")
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
        after = os.fstat(stream.fileno())
    def identity(s):
        return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if not identity(st) == identity(before) == identity(after) == identity(path.lstat()):
        raise ValueError("Installer changed during verification")
    if digest != asset.digest:
        raise ValueError("Installer digest mismatch")
    return identity(st)

def verify_installer(path, asset, *, tag, current, prerelease, trusted_signers=TRUSTED_SIGNERS,
                     signature_reader=windows_signature):
    """Return evidence only; caller must secure staging and revalidate before launch."""
    if not isinstance(asset, Asset) or eligible_release(
            {"tag_name":tag, "draft":False, "prerelease":prerelease}, current) is None:
        raise ValueError("Update channel/version rejected")
    expected = asset_from_release(tag, {"name":asset.name, "browser_download_url":asset.url,
                                       "size":asset.size, "digest":"sha256:"+asset.digest})
    if expected != asset:
        raise ValueError("Asset identity rejected")
    if not trusted_signers or any(not isinstance(p, str) or not re.fullmatch(r"[0-9a-f]{64}", p)
                                  for p in trusted_signers):
        raise ValueError("Publisher trust is not provisioned")
    path = Path(os.path.abspath(path))
    if path.name != asset.name:
        raise ValueError("Installer filename mismatch")
    identity = _identity(path, asset)
    signature = signature_reader(path)
    if not isinstance(signature, SignatureEvidence) or signature.status != "Valid":
        raise ValueError("Authenticode signature not valid")
    if signature.certificate_sha256 not in trusted_signers:
        raise ValueError("Signer not trusted")
    if _identity(path, asset) != identity:
        raise ValueError("Installer changed during signature verification")
    return signature
