"""Developer-only, asserted Karnaugh map and synthesized circuit evidence."""
from pathlib import Path
from boolean_synthesis import synthesize
from logic_exercise import read_exercise

EXAMPLES = Path(__file__).resolve().parent / "examples"


def capture_karnaugh(app, lab, output, language, theme):
    """Use a disposable Logic Lab after its standard captures are complete."""
    lab.select_tool("karnaugh")
    view = lab.karnaugh
    view.width.setCurrentIndex(view.width.findData(4))
    view.form.setCurrentIndex(view.form.findData("SOP"))
    view.reset()
    corners = (0,2,8,10)
    for index in corners:
        view.cycle(index)
    if (view.solution.expression != "B'D'" or len(view.solution.groups) != 1
            or tuple(view.solution.groups[0].cells) != corners):
        raise RuntimeError("Expected four-corner Karnaugh group")
    if {i for i,b in view.cells.items() if b.property("groupSelected")} != set(corners):
        raise RuntimeError("Karnaugh group selection not reflected in cells")
    app.processEvents()
    for c,header in enumerate(view.column_headers):
        cell=view.cells[view.matrix[0][c]]
        if header.height()>=cell.height() or abs(header.geometry().center().x()-cell.geometry().center().x())>2:
            raise RuntimeError("Karnaugh header is not compact and aligned")
    _save(lab, output / f"{language}-{theme}-karnaugh-corners.png")

    # Explicit developer-only installation into the disposable lab.
    document = synthesize(view.values, "SOP")
    lab.install_document(document, False)
    lab.select_tool("gates")
    lab.diagram.fit()
    if tuple(i for i,(_,out) in enumerate(lab.circuit.truth_table()) if out[0]) != corners:
        raise RuntimeError("Synthesized circuit does not match selected corners")
    app.processEvents()
    _save(lab, output / f"{language}-{theme}-karnaugh-synthesized.png")

    lab.select_tool("state-design")
    state=lab.state_design
    state.width.setCurrentIndex(state.width.findData(2))
    state.ff.setCurrentIndex(state.ff.findData("JK"))
    state.input.setCurrentIndex(1)
    state.clock.click()
    if state.state!=1 or state.graph.state!=1 or not state.trace:
        raise RuntimeError("Expected executed FSM clock transition")
    app.processEvents()
    _save(lab, output / f"{language}-{theme}-state-design-clock.png")

    # Load shipped fixtures through the same validated file reader as the UI.
    lab.select_tool("karnaugh")
    exercise = read_exercise(EXAMPLES / "karnaugh-dont-care.mano-exercise.json", "karnaugh")
    view.apply_exercise(exercise)
    view.results.setCurrentWidget(view.proof)
    app.processEvents()
    if view.exercise() != exercise or view.proof.rowCount() != len(exercise.values):
        raise RuntimeError("Expected imported POS exercise")
    for i, value in enumerate(exercise.values):
        expected = "X" if value is None else str(value)
        cover = str(view.solution.evaluate(i))
        actual = tuple(view.proof.item(i, c).text() for c in range(4))
        if actual != (str(i), expected, cover, cover) or (value is not None and cover != expected):
            raise RuntimeError("Karnaugh verification table disagrees with exercise")
    _save(lab, output / f"{language}-{theme}-karnaugh-verify.png")

    lab.select_tool("state-design")
    exercise = read_exercise(EXAMPLES / "fsm-moore-reduction.mano-exercise.json", "state-design")
    state.apply_exercise(exercise)
    state.views.setCurrentWidget(state.analysis_text)
    app.processEvents()
    if (state.exercise() != exercise or state.analysis.paths != ((0,""),(1,"1"))
            or state.analysis.unreachable != (2,3) or state.analysis.classes != ((0,1),(2,3))):
        raise RuntimeError("Unexpected FSM analysis for shipped exercise")
    _save(lab, output / f"{language}-{theme}-state-design-analysis.png")

    state.views.setCurrentWidget(state.reduction_text)
    app.processEvents()
    if (state.reduction.groups != ((0,1),) or state.reduction.bits != 0
            or state.encoding.codes != (0,) or state.encoding.unused != (1,)
            or any(state.encoding.design.step(1,x) != (0,0) for x in (0,1))
            or state.trace or state.state != 0 or state.exercise() != exercise):
        raise RuntimeError("Expected behavior-preserving reduced implementation")
    _save(lab, output / f"{language}-{theme}-state-design-reduction.png")


def _save(lab, target):
    image = lab.grab()
    if image.isNull() or not image.save(str(target)):
        raise RuntimeError(f"Could not save {target}")
