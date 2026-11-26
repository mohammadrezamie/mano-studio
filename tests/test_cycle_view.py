import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication

from simulator import CPU
from ui.cycle_view import CycleView


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("fa", [False, True])
def test_cycle_view_inspects_actual_cpu_groups_without_mutating_machine(app, fa):
    cpu = CPU({0: 0x2100, 0x100: 0x1234})
    event = cpu.step()
    registers = cpu.registers().copy()
    memory = cpu.memory.copy()
    calls = []
    view = CycleView(fa, lambda: calls.append("next"), lambda: calls.append("back"))
    try:
        view.show_event(event)
        assert view.current_trace is event
        assert view.groups.rowCount() == len(event.microevents) == 6
        assert view.groups.currentRow() == 0
        assert view.groups.item(0, 0).text() == "T0"
        assert view.groups.item(4, 1).text() == view.t("Execute", "اجرا")
        assert view.groups.item(5, 2).text() == "AC ← DR"

        view.groups.setCurrentCell(4, 0)
        group = event.microevents[4]
        assert view.bus.control is group.control
        assert view.detail.rowCount() == len(group.before)
        assert "M[100] = 1234" in view.memory.text()
        assert "M.READ" in view.controls.text()
        assert view.detail.item(0, 0).text() in group.before

        view.back_button.click()
        view.step_button.click()
        assert calls == ["back", "next"]
        assert cpu.registers() == registers
        assert cpu.memory == memory

        assert view.groups.accessibleName() == view.t(
            "Recorded timing groups", "گروه‌های زمانی ثبت‌شده")
        assert view.detail.accessibleName() == view.t(
            "Register state changes", "تغییرات وضعیت ثبات‌ها")
        assert view.step_button.accessibleName() == view.t(
            "Next timing group", "گروه زمانی بعدی")
    finally:
        view.close()
        view.deleteLater()


def test_cycle_view_marks_partial_execution_and_clears_stale_trace(app):
    cpu = CPU({0: 0x2100, 0x100: 0x1234})
    for _ in range(3):
        cpu.microstep()
    pending = cpu.pending_event
    assert pending is not None and len(pending.microevents) == 3
    view = CycleView()
    try:
        view.show_event(pending, partial=True)
        assert view.groups.rowCount() == 3
        assert view.groups.currentRow() == 2
        assert "In progress" in view.title.text()
        view.show_event(None)
        assert view.current_trace is None
        assert view.groups.rowCount() == 0
        assert view.detail.rowCount() == 0
        assert view.bus.control is None
        assert not view.memory.text()
        assert not view.controls.text()
    finally:
        cpu.cancel_pending()
        view.close()
        view.deleteLater()
