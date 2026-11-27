"""Capture actual Qt workspace screenshots for visual review."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from render_preflight import configure_offscreen_fonts, check_fonts
configure_offscreen_fonts()
from pathlib import Path
import tempfile
import json
import hashlib
from time import perf_counter
from capture_lifecycle import dispose_capture_widget, discard_capture_lab
from unittest.mock import patch
from PySide6.QtWidgets import QMessageBox
from learning_catalog import TOOLS
from capture_karnaugh import capture_karnaugh
from visual_review import build_gallery, image_info
from ui.learning_center import LearningCenter
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication
from ui.logic_lab import LogicLab
from ui.program_lab import ProgramLab
from ui.workspace import Workspace


def capture_active_states(app,window,output,language):
    """Fresh sandboxes, explicit actions, and real model assertions before every image."""
    logic=LogicLab(window);computer=ProgramLab(window)
    logic.resize(1360,900);computer.resize(1360,900)
    records=[]
    def capture(lab,route,state,action,check):
        for other in (logic,computer):
            if other is not lab:other.hide()
        lab.select_tool(route);lab.show();app.processEvents()
        action()
        if not check():raise RuntimeError(f"Demo did not reach {route}/{state}")
        app.processEvents()
        target=output/f"{language}-dark-active-{route}-{state}.png"
        image=lab.grab()
        if image.isNull() or not image.save(str(target)):raise RuntimeError(f"Could not save {target}")
        width,height,digest=image_info(output,target.name)
        records.append(dict(language=language,theme="dark",route=route,state=state,image=target.name,
                            width=width,height=height,sha256=digest))
    try:
        def cpu():
            computer.example();computer.step()
            computer.datapath.focus.setChecked(True)
            computer.datapath.groups.setCurrentIndex(1)
            computer.pause()
        capture(computer,"live","fetch",cpu,lambda:computer.datapath.group.timing==1)
        def logic_wave():
            v=logic.sequential
            v.selector.setCurrentIndex(v.selector.findData("D"))
            v.reset();v.buttons["D"].setChecked(True);v.pulse()
            v.buttons["D"].setChecked(False);v.pulse()
        def lookahead():
            logic.selector.setCurrentIndex(logic.selector.findData("lookahead4"))
            for pin in ("A0","A1","A2","A3","Cin"):
                logic.buttons[pin].setChecked(True)
            logic.diagram.fit()
        capture(logic,"gates","lookahead-carry",lookahead,
            lambda:logic.circuit.result(logic.inputs)=={"S0":0,"S1":0,"S2":0,"S3":0,"Cout":1})
        capture(logic,"sequential","clocked",logic_wave,lambda:logic.sequential.model.value==0 and len(logic.sequential.waveform.rows)>=5)
        def excitation_reference():
            v=logic.sequential
            v.selector.setCurrentIndex(v.selector.findData("JK"))
            v.details.setCurrentWidget(v.reference)
        capture(logic,"sequential","jk-excitation",excitation_reference,
            lambda:logic.sequential.reference.excitation.item(2,2).text()=="X" and logic.sequential.reference.excitation.item(2,3).text()=="1")
        def sr_reference():
            v=logic.sequential
            v.selector.setCurrentIndex(v.selector.findData("SR"))
            v.details.setCurrentWidget(v.reference)
        capture(logic,"sequential","sr-forbidden",sr_reference,
            lambda:logic.sequential.reference.characteristic.item(3,3).text()==("ممنوع" if language=="fa" else "Forbidden"))
        def latch_unknown():
            v=logic.sequential
            v.details.setCurrentWidget(v.storage)
            l=v.storage
            l.selector.setCurrentIndex(l.selector.findData("SR_NOR"))
            l.reset()
            l.buttons["S"].setChecked(True);l.buttons["R"].setChecked(True);l.apply()
            l.buttons["S"].setChecked(False);l.buttons["R"].setChecked(False);l.apply()
        capture(logic,"sequential","latch-unknown",latch_unknown,
            lambda:logic.sequential.storage.state.q is None and logic.sequential.storage.history.rowCount()==2)
        def async_preset():
            v=logic.sequential
            v.details.setCurrentWidget(v.storage)
            l=v.storage
            l.selector.setCurrentIndex(l.selector.findData("D_ASYNC"))
            l.reset();l.buttons["PREbar"].setChecked(False);l.apply()
        capture(logic,"sequential","async-preset",async_preset,
            lambda:logic.sequential.storage.state.q==1 and logic.sequential.storage.previous_clock==0)
        logic.sequential.details.setCurrentIndex(0)
        capture(logic,"cache","conflict",logic.cache.example,lambda:logic.cache.model.accesses==6 and logic.cache.model.misses==6)
        paging=logic.address_translation.paging
        capture(logic,"virtual-memory","fault-reload",paging.example,lambda:paging.last.fault and paging.last.value==0xCAFE and paging.model.page_outs==1)
        serial=computer.io_organization.serial
        def serial_error():
            serial.parity.setCurrentIndex(1)
            serial.flip.setCurrentIndex(serial.flip.findData(1))
            serial.start();serial.finish()
        capture(computer,"serial","parity-error",serial_error,lambda:serial.model.result.parity_error and serial.model.fifo.empty)
        cross=computer.crossbar
        def parallel():
            cross.demo.setCurrentIndex(0);cross.example();cross.step()
        capture(computer,"crossbar","parallel-grants",parallel,lambda:len(cross.last.transfers)==4)
        sync=computer.synchronization
        def race():
            sync.mode.setCurrentIndex(1);sync.reset();sync.run()
        capture(computer,"synchronization","lost-update",race,lambda:sync.model.done and sync.model.shared==1 and sync.model.expected==2)
        def locked():
            sync.mode.setCurrentIndex(0);sync.reset();sync.run()
        capture(computer,"synchronization","atomic-lock",locked,lambda:sync.model.done and sync.model.shared==2)
        msi=computer.coherence
        def dirty_owner():
            msi.reset();msi.core.setValue(0);msi.address.setValue(3);msi.value.setValue(0xABCD)
            msi.access(True)
        capture(computer,"coherence","dirty-owner",dirty_owner,lambda:msi.model.lines[0][3].state=="M" and msi.model.memory[3]==0)
        def shared_read():
            dirty_owner();msi.core.setValue(1);msi.access(False)
        capture(computer,"coherence","shared-read",shared_read,lambda:msi.last.value==0xABCD and msi.model.memory[3]==0xABCD and msi.model.lines[0][3].state==msi.model.lines[1][3].state=="S")
        omega=computer.omega
        def omega_conflict():
            omega.size.setCurrentIndex(omega.size.findData(8));omega.example()
        capture(computer,"omega","internal-block",omega_conflict,lambda:len(omega.results)==2 and omega.results[0].granted and omega.results[1].blocked_stage==0)
        def omega_cross():
            omega.size.setCurrentIndex(omega.size.findData(2));omega.example()
        capture(computer,"omega","crossed-switch",omega_cross,lambda:len(omega.results)==2 and all(t.granted and t.hops[0].crossed for t in omega.results))
        laws=logic.karnaugh.laws
        def de_morgan():
            logic.karnaugh.results.setCurrentWidget(laws)
            laws.law.setCurrentIndex(laws.law.findData("de-morgan"))
            laws.dual.setChecked(True)
        capture(logic,"karnaugh","de-morgan-dual",de_morgan,
            lambda: "(A · B)'" in laws.equation.text() and all(laws.table.item(i,3).text()==laws.table.item(i,4).text() for i in range(8)))
        def static_hazard():
            v=logic.karnaugh
            v.form.setCurrentIndex(v.form.findData("SOP"))
            v.results.setCurrentWidget(v.analysis_panel)
            v.hazard_example()
        capture(logic,"karnaugh","static-hazard",static_hazard,
            lambda:"3 ↔ 7" in logic.karnaugh.analysis.toPlainText())
    finally:
        for lab in (logic,computer):
            discard_capture_lab(lab)
        app.processEvents()
    return records


def capture_routes(app,window,output):
    """Capture each distinct real route once per locale, with entry-to-image mapping."""
    records=[]
    active=[]
    window.themes.setCurrentIndex(window.themes.findData("dark"))
    for language in ("en","fa"):
        window.languages.setCurrentIndex(window.languages.findData(language))
        window.tabs.setCurrentIndex(0)
        app.processEvents()
        center=LearningCenter(window)
        center.resize(1100,750);center.show();app.processEvents()
        target=output/f"{language}-dark-learning-center.png"
        if not center.grab().save(str(target)):raise RuntimeError(f"Could not save {target}")
        dispose_capture_widget(center)
        logic=LogicLab(window);computer=ProgramLab(window)
        logic.resize(1360,900);computer.resize(1360,900)
        lab_by_name={"workspace":window,"logic":logic,"computer":computer}
        seen={}
        for tool in TOOLS:
            key=(tool.lab,tool.route)
            if key not in seen:
                lab=lab_by_name[tool.lab]
                # Keep only the active dialog visible, ensuring hidden timers stop.
                for other in (logic,computer):
                    if other is not lab:other.hide()
                if tool.lab!="workspace":
                    lab.select_tool(tool.route);lab.show()
                else:window.show()
                app.processEvents()
                if tool.route=="gates":
                    logic.diagram.fit();app.processEvents()
                target=output/f"{language}-dark-route-{tool.lab}-{tool.route}.png"
                image=lab.grab()
                if image.isNull() or not image.save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                seen[key]={"image":target.name,"width":image.width(),"height":image.height(),
                           "sha256":hashlib.sha256(target.read_bytes()).hexdigest()}
            records.append({"entry":tool.id,"chapter":tool.chapter,"language":language,
                            "theme":"dark","lab":tool.lab,"route":tool.route,**seen[key]})
        for dialog in (logic,computer):
            discard_capture_lab(dialog)
        app.processEvents()
        active.extend(capture_active_states(app,window,output,language))
    (output/"route-manifest.json").write_text(json.dumps({
        "kind":"actual Qt offscreen render; not manual visual acceptance",
        "entries":records,"active_states":active},ensure_ascii=False,indent=2),encoding="utf-8")


def capture_all():
    app = QApplication([])
    app.setStyle("Fusion")
    output = Path("screenshots")
    output.mkdir(exist_ok=True)
    evidence=check_fonts(app)
    (output/"font-preflight.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
    with tempfile.TemporaryDirectory() as directory:
        settings = QSettings(str(Path(directory) / "settings.ini"), QSettings.Format.IniFormat)
        window = Workspace(settings)
        window.apply_appearance()
        window.resize(1360, 900)
        window.editor.setPlainText("AC ← M[100]\nAC ← AC + M[101]\nM[102] ← AC\nS ← 0")
        window.run_translation()
        window.show()
        for language in ("en", "fa"):
            window.languages.setCurrentIndex(1 if language == "fa" else 0)
            for theme in ("dark", "light", "night"):
                started=perf_counter()
                window.themes.setCurrentIndex(window.themes.findData(theme))
                # Real localized About screen, independently of modal interaction.
                about = window.about_dialog()
                about.show()
                app.processEvents()
                target = output / f"{language}-{theme}-about.png"
                if not about.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                image_info(output, target.name)
                dispose_capture_widget(about)
                app.processEvents()
                for tab, mode in enumerate(("editor", "pad", "builder")):
                    window.tabs.setCurrentIndex(tab)
                    app.processEvents()
                    target = output / f"{language}-{theme}-{mode}.png"
                    if not window.grab().save(str(target)):
                        raise RuntimeError(f"Could not save {target}")
                window.editor.document().setModified(False)
                window.direction_box.setCurrentIndex(1)
                window.editor.setPlainText("LDA 100 I\nADD 101\nSTA 102\nHLT")
                window.run_translation()
                window.tabs.setCurrentIndex(0)
                app.processEvents()
                target=output/f"{language}-{theme}-reverse.png"
                if not window.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                window.editor.document().setModified(False)
                window.direction_box.setCurrentIndex(0)
                window.editor.setPlainText("AC ← M[100]\nAC ← AC + M[101]\nM[102] ← AC\nS ← 0")
                window.run_translation()
                # Capture actual optional labs too, without opening modal exec loops.
                lab=LogicLab(window)
                lab.resize(1360,900)
                lab.selector.setCurrentIndex(lab.selector.findData("full_adder"))
                lab.show()
                app.processEvents()
                lab.diagram.fit()
                lab.choose_row(5,0)
                app.processEvents()
                target=output/f"{language}-{theme}-logic.png"
                if not lab.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                lab.canvas_edit.setChecked(True)
                app.processEvents()
                target=output/f"{language}-{theme}-logic-edit.png"
                if not lab.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                lab.canvas_edit.setChecked(False)
                lab.mode_tabs.setCurrentIndex(1)
                lab.sequential.buttons["D"].setChecked(True)
                lab.sequential.pulse()
                app.processEvents()
                target=output/f"{language}-{theme}-sequential.png"
                if not lab.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                capture_karnaugh(app,lab,output,language,theme)
                discard_capture_lab(lab)
                computer=ProgramLab(window)
                computer.resize(1360,900)
                computer.show()
                computer.step()
                computer.step()
                computer.pause()
                app.processEvents()
                target=output/f"{language}-{theme}-computer.png"
                if not computer.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                for tab,suffix in ((2,"debugger"),(3,"alu")):
                    computer.inspector.setCurrentIndex(tab)
                    app.processEvents()
                    target=output/f"{language}-{theme}-{suffix}.png"
                    if not computer.grab().save(str(target)):
                        raise RuntimeError(f"Could not save {target}")
                computer.arithmetic.op.setCurrentIndex(0)
                app.processEvents()
                target=output/f"{language}-{theme}-bases.png"
                if not computer.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                discard_capture_lab(computer)
                app.processEvents()
                print(f'Captured {language}/{theme}: {perf_counter()-started:.3f}s', flush=True)
        started=perf_counter()
        capture_routes(app,window,output)
        build_gallery(output)
        print(f'Captured and validated all routes: {perf_counter()-started:.3f}s', flush=True)
        window.editor.document().setModified(False)
        dispose_capture_widget(window)


def main():
    # Unexpected modal prompts must fail, not hang or be auto-accepted.
    def unexpected(*args, **kwargs):
        raise RuntimeError("Unexpected message box during capture: " + str(args[1:3]))
    from contextlib import ExitStack
    with ExitStack() as stack:
        for name in ("question", "warning", "information", "critical"):
            stack.enter_context(patch.object(QMessageBox, name, side_effect=unexpected))
        capture_all()


if __name__ == "__main__":
    main()
