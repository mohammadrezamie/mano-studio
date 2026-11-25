"""Developer-only, asserted Karnaugh map and synthesized circuit evidence."""
from boolean_synthesis import synthesize


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


def _save(lab, target):
    image = lab.grab()
    if image.isNull() or not image.save(str(target)):
        raise RuntimeError(f"Could not save {target}")
