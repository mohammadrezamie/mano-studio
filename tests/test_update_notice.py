"""Local notification and parser tests; no external network."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import json
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from ui.workspace import Workspace
from ui.update_notice import OPT_IN, LAST_NOTICE
from update_service import parse_release_payload

@pytest.fixture
def window(tmp_path):
    app = QApplication.instance() or QApplication([])
    w = Workspace(QSettings(str(tmp_path / "notice.ini"), QSettings.Format.IniFormat))
    yield w
    w.editor.document().setModified(False)
    w.close()

def test_default_off(window):
    notice = window.update_notice
    notice.schedule()
    notice.check()
    assert not notice.delay.isActive() and notice.reply is None and not notice.checked
    assert notice.button.isHidden()

def test_notice_consent_and_relabel(window, monkeypatch):
    import update_service
    monkeypatch.setattr(update_service, "VERSION", "1.0.0")
    rows = [{"tag_name":"v1.0.1","draft":False,"prerelease":False},
            {"tag_name":"v9.0.0","draft":True,"prerelease":False},
            {"tag_name":"v2.0.0-beta.1","draft":False,"prerelease":True}]
    release = parse_release_payload(json.dumps(rows).encode())
    assert release.tag == "v1.0.1"
    notice = window.update_notice
    notice.show_release(release)
    assert notice.button.isHidden()
    notice.set_enabled(True)
    assert window.settings.value(OPT_IN, False, type=bool)
    assert notice.delay.isActive()
    notice.delay.stop()
    notice.show_release(release)
    assert not notice.button.isHidden()
    assert window.settings.value(LAST_NOTICE) == release.tag
    window.languages.setCurrentIndex(window.languages.findData("fa"))
    assert "به‌روزرسانی" in notice.button.text()
    notice.set_enabled(False)
    assert notice.button.isHidden() and notice.reply is None
    assert not notice.delay.isActive()

def test_response_limit():
    with pytest.raises(ValueError):
        parse_release_payload(b" " * 2_000_001)
