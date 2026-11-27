"""Offscreen UI contract; no real networking or installer execution."""
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
from threading import Event
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from ui.workspace import Workspace
from ui.preferences import Preferences, DownloadWorker
from update_download import DownloadCancelled


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("language",["en","fa"])
def test_progress_cancel_dialog(app,tmp_path,language):
    workspace=Workspace(QSettings(str(tmp_path/"settings.ini"),QSettings.Format.IniFormat))
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    dialog=Preferences(workspace)
    try:
        dialog.stop=Event()
        dialog.show_progress(50,100)
        assert dialog.download_progress.value()==50
        dialog.show_progress(100,100)
        assert dialog.download_progress.value()==99
        dialog.cancel_download()
        assert dialog.stop.is_set() and not dialog.cancel_download_button.isEnabled()
        dialog.show_progress(10,100)
        assert dialog.download_progress.value()==99
        dialog.download_result(None,"cancelled")
        assert dialog.download_progress.isHidden()
        dialog.stop=Event()
        dialog.download_result(tmp_path/"verified.exe","")
        assert dialog.download_progress.value()==100
    finally:
        dialog.close()
        workspace.editor.document().setModified(False)
        workspace.close()


def test_worker_progress_and_cancel(monkeypatch,tmp_path):
    from ui import preferences
    stop=Event()
    path=tmp_path/"verified.exe"
    worker=DownloadWorker(object(),path,stop)
    progress=[]
    finished=[]
    worker.progress.connect(lambda n,t:progress.append((n,t)))
    worker.finished.connect(lambda p,e:finished.append((p,e)))
    def fake(asset,destination,*,explicit,cancelled,progress):
        assert explicit and destination==path
        assert not cancelled()
        for n in (0,1,2,10,1000):
            progress(n,1000)
        stop.set()
        assert cancelled()
        raise DownloadCancelled()
    monkeypatch.setattr(preferences,"download",fake)
    worker.run()
    assert progress==[(0,1000),(10,1000),(1000,1000)]
    assert finished==[(None,"cancelled")]
