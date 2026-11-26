import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QPushButton

from instruction_catalog import TEMPLATES
from ui.workspace import Workspace


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def make_workspace(tmp_path, language):
    settings = QSettings(str(tmp_path / f"settings-{language}.ini"),
                         QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    return Workspace(settings)


@pytest.mark.parametrize("language", ["en", "fa"])
def test_guided_builder_previews_all_25_instructions_and_indirect_forms(
        app, tmp_path, language):
    workspace = make_workspace(tmp_path, language)
    try:
        assert workspace.operations.count() == 25
        for mnemonic, template in TEMPLATES.items():
            index = workspace.operations.findData(mnemonic)
            assert index >= 0, mnemonic
            workspace.operations.setCurrentIndex(index)
            workspace.address.setText("ABC")
            workspace.indirect.setChecked(False)
            workspace.update_preview()
            assert workspace.insert_button.isEnabled(), (
                mnemonic, workspace.preview.text())
            assert "→" in workspace.preview.text()
            if "{a}" in template:
                workspace.indirect.setChecked(True)
                workspace.update_preview()
                assert workspace.insert_button.isEnabled(), (
                    mnemonic, "indirect", workspace.preview.text())
            else:
                assert not workspace.address.isEnabled()
                assert not workspace.indirect.isEnabled()
    finally:
        workspace.editor.document().setModified(False)
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_symbol_pad_and_builder_hex_pad_construct_program_without_keyboard(
        app, tmp_path, language):
    workspace = make_workspace(tmp_path, language)
    try:
        pad_page = workspace.tabs.widget(1)
        pad_buttons = {button.text(): button
                       for button in pad_page.findChildren(QPushButton)}
        required = {
            "AC", "PC", "AR", "DR", "E", "IR", "TR", "INPR", "OUTR",
            "IEN", "FGI", "FGO", "S", "M[", "]", "[", "←", "=", "+",
            "∧", "¬", "(", ")", ":", ",", "IF", "THEN", "CIR", "CIL",
        }
        required.update(workspace.t(label) for label in
                        ("Space", "Enter", "Backspace", "Undo", "Redo"))
        assert required.issubset(pad_buttons)

        workspace.editor.clear()
        workspace.tabs.setCurrentIndex(1)
        for token in ("AC", workspace.t("Space"), "←", workspace.t("Space"),
                      "M[", "1", "0", "0", "]"):
            pad_buttons[token].click()
        assert workspace.editor.toPlainText() == "AC ← M[100]"
        workspace.run_translation()
        assert workspace.output.toPlainText() == "LDA 100"

        workspace.editor.clear()
        workspace.tabs.setCurrentIndex(2)
        workspace.operations.setCurrentIndex(workspace.operations.findData("LDA"))
        address_buttons = {
            button.text(): button
            for button in workspace.tabs.widget(2).findChildren(QPushButton)
        }
        for token in "0123456789ABCDEF":
            workspace.address.clear()
            address_buttons[token].click()
            assert workspace.address.text() == token
        workspace.address.clear()
        for token in "ABC":
            address_buttons[token].click()
        workspace.indirect.setChecked(True)
        assert workspace.address.text() == "ABC"
        assert workspace.insert_button.isEnabled()
        workspace.insert_instruction()
        assert workspace.editor.toPlainText() == "AC ← M[M[ABC]]\n"
        workspace.run_translation()
        assert workspace.output.toPlainText() == "LDA ABC I"
    finally:
        workspace.editor.document().setModified(False)
        workspace.close()
