import hashlib
import io
import pytest
from update_download import asset_from_release, download, allowed_url, SafeRedirect

TAG='v0.3.1-beta.1'
NAME='ManoStudio-Setup-v0.3.1-beta.1-x64.exe'
URL='https://github.com/mohammadrezamie/mano-studio/releases/download/'+TAG+'/'+NAME
DATA=b'test fixture, not an executable'


def metadata(**changes):
    return dict({'name':NAME,'browser_download_url':URL,'size':len(DATA),'digest':'sha256:'+hashlib.sha256(DATA).hexdigest()},**changes)


class Response(io.BytesIO):
    def __init__(self,data,url=URL):
        super().__init__(data)
        self.url=url
    def geturl(self):
        return self.url


def test_success_and_no_overwrite(tmp_path):
    asset=asset_from_release(TAG,metadata())
    path=tmp_path/NAME
    assert download(asset,path,explicit=True,opener=lambda *a,**k:Response(DATA))==path
    assert path.read_bytes()==DATA
    with pytest.raises(FileExistsError):
        download(asset,path,explicit=True,opener=lambda *a,**k:pytest.fail('network'))


def test_consent(tmp_path):
    with pytest.raises(PermissionError):
        download(asset_from_release(TAG,metadata()),tmp_path/NAME,opener=lambda *a,**k:pytest.fail('network'))


@pytest.mark.parametrize('changes',[{'name':'other.exe'},{'browser_download_url':'https://evil.example/a.exe'},
    {'digest':None},{'digest':'sha256:abc'},{'size':True},{'size':0},{'size':999999999}])
def test_reject_metadata(changes):
    assert asset_from_release(TAG,metadata(**changes)) is None


@pytest.mark.parametrize('data',[DATA[:-1],DATA+b'x',b'x'*len(DATA)])
def test_bad_bytes_cleanup(tmp_path,data):
    with pytest.raises(ValueError):
        download(asset_from_release(TAG,metadata()),tmp_path/NAME,explicit=True,opener=lambda *a,**k:Response(data))
    assert not list(tmp_path.iterdir())


def test_untrusted_response(tmp_path):
    with pytest.raises(ValueError):
        download(asset_from_release(TAG,metadata()),tmp_path/NAME,explicit=True,opener=lambda *a,**k:Response(DATA,'https://evil.example/a.exe'))
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('url',['http://github.com/a','https://github.com.evil.example/a','https://user@github.com/a','https://github.com:444/a'])
def test_disallow_url(url):
    assert not allowed_url(url)
    with pytest.raises(ValueError):
        SafeRedirect().redirect_request(None,None,302,'',{},url)


@pytest.mark.parametrize("url", [None, "", 42, "https://[broken", "https://github.com:abc/a", "https://github.com:65536/a", "https://github.com/a#fragment", " https://github.com/a", "https://git\nhub.com/a", "https://github.com\\a", "https://github.com/a\x7f"])
def test_malformed_url_is_rejected(url):
    assert allowed_url(url) is False


@pytest.mark.parametrize("url", ["https://github.com/a", "https://github.com:443/a", "https://release-assets.githubusercontent.com/a?sig=abc%20def", "https://objects.githubusercontent.com/a"])
def test_official_asset_hosts_still_allowed(url):
    assert allowed_url(url) is True


@pytest.mark.parametrize("field,value", [
    ("url", None), ("url", 1), ("name", None),
    ("size", True), ("size", "42"), ("digest", None), ("digest", 123),
])
def test_malformed_asset_types_fail_before_network(tmp_path, field, value):
    from dataclasses import replace
    asset = replace(asset_from_release(TAG, metadata()), **{field: value})
    with pytest.raises(ValueError, match="Invalid asset metadata types"):
        download(asset, tmp_path/NAME, explicit=True,
                 opener=lambda *a, **k: pytest.fail("unexpected network"))
    assert not list(tmp_path.iterdir())


def test_cancel_after_progress_cleans_partial(tmp_path):
    from update_download import DownloadCancelled
    seen = []
    with pytest.raises(DownloadCancelled):
        download(asset_from_release(TAG, metadata()), tmp_path/NAME,
                 explicit=True, opener=lambda *a, **k: Response(DATA),
                 progress=lambda count, total: seen.append((count, total)),
                 cancelled=lambda: bool(seen and seen[-1][0]))
    assert seen == [(0, len(DATA)), (len(DATA), len(DATA))]
    assert not list(tmp_path.iterdir())


def test_destination_created_during_download_is_preserved(tmp_path):
    path = tmp_path/NAME
    def progress(count, total):
        if count == total:
            path.write_bytes(b"existing user data")
    with pytest.raises(FileExistsError):
        download(asset_from_release(TAG, metadata()), path,
                 explicit=True, opener=lambda *a, **k: Response(DATA),
                 progress=progress)
    assert path.read_bytes() == b"existing user data"
    assert list(tmp_path.iterdir()) == [path]


def test_timeout_after_read_cleans_partial(tmp_path, monkeypatch):
    import update_download
    clock = [0]
    monkeypatch.setattr(update_download, "monotonic", lambda: clock[0])
    class SlowResponse(Response):
        def read(self, size):
            clock[0] = update_download.MAX_SECONDS + 1
            return super().read(size)
    with pytest.raises(TimeoutError):
        download(asset_from_release(TAG, metadata()), tmp_path/NAME,
                 explicit=True, opener=lambda *a, **k: SlowResponse(DATA))
    assert not list(tmp_path.iterdir())
