"""Optional startup update notice; no download or installer execution."""
from PySide6.QtCore import QObject, QTimer, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import QPushButton
from update_service import RELEASES_URL, parse_release_payload

OPT_IN = "updates/auto_check"
LAST_NOTICE = "updates/last_notified"
MAX_BYTES = 2_000_000


class UpdateNotice(QObject):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.workspace = workspace
        self.settings = workspace.settings
        self.manager = QNetworkAccessManager(self)
        self.reply = None
        self.checked = False
        self.payload = bytearray()
        self.release = None
        self.button = QPushButton()
        self.button.clicked.connect(workspace.open_preferences)
        workspace.statusBar().addPermanentWidget(self.button)
        self.button.hide()
        self.delay = QTimer(self)
        self.delay.setSingleShot(True)
        self.delay.timeout.connect(self.check)
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.timeout.connect(self.cancel)

    def enabled(self):
        return self.settings.value(OPT_IN, False, type=bool)

    def schedule(self):
        if self.enabled() and not self.checked:
            self.delay.start(1500)

    def set_enabled(self, enabled):
        self.settings.setValue(OPT_IN, bool(enabled))
        self.settings.sync()
        if not enabled:
            self.cancel()
            self.release = None
            self.button.hide()
        else:
            self.schedule()

    def check(self):
        if not self.enabled() or self.checked or self.reply is not None:
            return
        self.checked = True
        request = QNetworkRequest(QUrl(RELEASES_URL))
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"User-Agent", b"ManoStudio-UpdateNotice")
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,
                             QNetworkRequest.RedirectPolicy.ManualRedirectPolicy)
        request.setTransferTimeout(6000)
        self.payload.clear()
        reply = self.manager.get(request)
        self.reply = reply
        reply.setReadBufferSize(65536)
        reply.readyRead.connect(self.read)
        reply.finished.connect(self.finished)
        self.deadline.start(10000)

    def read(self):
        reply = self.reply
        if reply is None:
            return
        chunk = bytes(reply.read(MAX_BYTES + 1 - len(self.payload)))
        self.payload.extend(chunk)
        if len(self.payload) > MAX_BYTES:
            self.cancel()

    def finished(self):
        reply = self.reply
        if reply is None:
            return
        self.read()
        if self.reply is not reply:
            return
        self.reply = None
        self.deadline.stop()
        try:
            if (self.enabled() and reply.error() == QNetworkReply.NetworkError.NoError
                    and reply.url().toString() == RELEASES_URL
                    and reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) == 200):
                release = parse_release_payload(bytes(self.payload))
                if release:
                    self.show_release(release)
        except (ValueError, TypeError, UnicodeError):
            pass
        finally:
            self.payload.clear()
            reply.deleteLater()

    def show_release(self, release):
        if not self.enabled():
            return
        self.release = release
        self.relabel()
        self.button.show()
        if self.settings.value(LAST_NOTICE, "") != release.tag:
            self.workspace.statusBar().showMessage(self.button.text(), 10000)
            self.settings.setValue(LAST_NOTICE, release.tag)
            self.settings.sync()

    def relabel(self):
        if self.release is not None:
            prefix = "به‌روزرسانی موجود: " if self.workspace.language == "fa" else "Update available: "
            self.button.setText(prefix + self.release.tag)

    def cancel(self):
        self.delay.stop()
        self.deadline.stop()
        reply, self.reply = self.reply, None
        self.payload.clear()
        if reply is not None:
            reply.abort()
            reply.deleteLater()
