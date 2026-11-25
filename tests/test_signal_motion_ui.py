import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QAbstractAnimation
from logic_engine import basic
from ui.logic_lab import LogicDiagram
from ui.motion import set_reduced_motion


def test_logic_motion_tracks_evaluated_changes():
    app = QApplication.instance() or QApplication([])
    previous = bool(app.property("manoReducedMotion"))
    view = LogicDiagram("dark")
    circuit = basic("NOT")
    view.resize(700, 400)
    view.show()
    try:
        set_reduced_motion(app, False)
        view.draw(circuit, circuit.evaluate({"A": 0}))
        assert not view._changed_paths
        view.draw(circuit, circuit.evaluate({"A": 1}))
        assert {net for net, _ in view._changed_paths} == {"A", "q"}
        assert view._net_animation.state() == QAbstractAnimation.State.Running
        assert not view.grab().isNull()
        set_reduced_motion(app, True)
        assert not view._changed_paths
        assert view._net_animation.state() == QAbstractAnimation.State.Stopped
        view.draw(circuit, circuit.evaluate({"A": 0}))
        assert not view._changed_paths
        set_reduced_motion(app, False)
        view.draw(circuit, circuit.evaluate({"A": 1}))
        view.set_editing(True)
        assert not view._changed_paths
        view.draw(circuit, circuit.evaluate({"A": 0}))
        assert not view._changed_paths
        view.set_editing(False)
        view.draw(circuit, circuit.evaluate({"A": 1}))
        view.hide()
        assert not view._changed_paths
    finally:
        view.close()
        set_reduced_motion(app, previous)


@pytest.mark.parametrize("fa", [False, True])
def test_lab_signal_motion_disabled_preserves_evaluated_values(fa):
    app = QApplication.instance() or QApplication([])
    previous = bool(app.property("manoReducedMotion"))
    view = LogicDiagram("dark", fa, reduced_motion=True)
    circuit = basic("NOT")
    view.show()
    try:
        set_reduced_motion(app, False)
        for bit in (0, 1, 0):
            values = circuit.evaluate({"A": bit})
            view.draw(circuit, values)
            assert view._last_values == values
            assert values["q"] == 1 - bit
            assert not view._changed_paths
            assert view._net_animation.state() == QAbstractAnimation.State.Stopped
    finally:
        view.close()
        set_reduced_motion(app, previous)
