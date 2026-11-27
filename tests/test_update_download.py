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
