from threading import Event
import hashlib
import io
import pytest
import update_download as service
from test_update_download import metadata, TAG, NAME, Response


def fixture(data):
    return service.asset_from_release(TAG, metadata(size=len(data), digest='sha256:'+hashlib.sha256(data).hexdigest()))


def test_progress(tmp_path):
    data=b'a'*150000
    updates=[]
    path=tmp_path/NAME
    service.download(fixture(data),path,explicit=True,opener=lambda *a,**k:Response(data),progress=lambda n,total:updates.append((n,total)))
    assert updates==[(n,len(data)) for n in (0,65536,131072,150000)]
    assert path.read_bytes()==data


def test_cancel_before_network(tmp_path):
    with pytest.raises(service.DownloadCancelled):
        service.download(fixture(b'a'),tmp_path/NAME,explicit=True,cancelled=lambda:True,opener=lambda *a,**k:pytest.fail('network'))
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('threshold',[0,65536,150000])
def test_cancel_during_progress(tmp_path,threshold):
    data=b'a'*150000
    stop=Event()
    def progress(n,total):
        if n>=threshold:
            stop.set()
    with pytest.raises(service.DownloadCancelled):
        service.download(fixture(data),tmp_path/NAME,explicit=True,opener=lambda *a,**k:Response(data),cancelled=stop.is_set,progress=progress)
    assert not list(tmp_path.iterdir())


def test_deadline_after_read(tmp_path,monkeypatch):
    time=[0]
    monkeypatch.setattr(service,'monotonic',lambda:time[0])
    class Slow(Response):
        def read(self,n):
            time[0]=service.MAX_SECONDS
            return super().read(n)
    with pytest.raises(TimeoutError):
        service.download(fixture(b'a'),tmp_path/NAME,explicit=True,opener=lambda *a,**k:Slow(b'a'))
    assert not list(tmp_path.iterdir())


def test_destination_race(tmp_path):
    path=tmp_path/NAME
    def progress(n,total):
        if n==total:
            path.write_bytes(b'original')
    with pytest.raises(FileExistsError):
        service.download(fixture(b'a'),path,explicit=True,opener=lambda *a,**k:Response(b'a'),progress=progress)
    assert path.read_bytes()==b'original'
    assert list(tmp_path.iterdir())==[path]
