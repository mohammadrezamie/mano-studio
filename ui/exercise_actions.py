"""Bilingual exercise file actions shared by Chapter 1 design tools."""
from pathlib import Path
import sys
from PySide6.QtWidgets import QFileDialog, QMessageBox, QPushButton, QMenu
from native_exercise import load as read_exercise, save as write_exercise


def add_exercise_actions(view, layout, kind):
    """Only explicit user actions read/write files; validate before replacing."""
    def t(en, fa):
        return fa if view.fa else en

    file_filter = t("Mano Studio (*.mano)", "مانو استودیو (*.mano)") + ";;" + t("Legacy exercise (*.mano-exercise.json)", "تمرین قدیمی (*.mano-exercise.json)") + ";;JSON (*.json)"

    def open_file():
        name, _ = QFileDialog.getOpenFileName(view, t("Open exercise", "باز کردن تمرین"), "", file_filter)
        if name:
            open_path(name)

    def open_path(name):
        try:
            exercise = read_exercise(name, kind)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(view, t("Cannot open exercise", "باز کردن تمرین ناموفق بود"),
                                t("Invalid, incompatible or unreadable exercise. Current design is unchanged.",
                                  "فایل تمرین نامعتبر، ناسازگار یا خواندنی نیست. طرح فعلی تغییر نکرد."))
            return
        answer = QMessageBox.question(view, t("Replace exercise?", "جایگزینی تمرین؟"),
                                      t("Replace the current exercise with the selected file?",
                                        "تمرین فعلی با فایل انتخاب‌شده جایگزین شود؟"),
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            view.apply_exercise(exercise)

    def save_file():
        name, _ = QFileDialog.getSaveFileName(view, t("Save exercise", "ذخیره تمرین"),
                                               kind+".mano", file_filter)
        if not name:
            return
        path = Path(name)
        if not path.suffix:
            path = path.with_suffix(".mano")
        try:
            write_exercise(path, view.exercise())
        except (OSError, ValueError):
            QMessageBox.warning(view, t("Cannot save exercise", "ذخیره تمرین ناموفق بود"),
                                t("Check the destination and permissions. Your current design is unchanged.",
                                  "مسیر و مجوز نوشتن را بررسی کنید. طرح فعلی تغییر نکرده است."))

    view.open_exercise_button = QPushButton(t("Open exercise", "باز کردن تمرین"))
    view.save_exercise_button = QPushButton(t("Save exercise", "ذخیره تمرین"))
    view.open_exercise_button.clicked.connect(open_file)
    view.save_exercise_button.clicked.connect(save_file)
    layout.addWidget(view.open_exercise_button)
    layout.addWidget(view.save_exercise_button)

    # The same original saved files are shipped with the offline examples.
    samples = {
        "karnaugh": (("majority", "Three-input majority", "اکثریت سه‌ورودی"),),
        "state-design": (
            ("overlap-101", "Overlapping 101 detector", "آشکارساز هم‌پوشان 101"),
            ("parity", "Odd parity detector", "تشخیص تعداد فرد بیت یک"),
        ),
    }
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    view.sample_exercise_button = QPushButton(t("Saved examples", "نمونه‌های ذخیره‌شده"))
    menu = QMenu(view.sample_exercise_button)
    for key, en, fa in samples.get(kind, ()):
        path = root / "examples" / "design" / (key + ".mano")
        menu.addAction(t(en, fa), lambda checked=False, p=path: open_path(p))
    view.sample_exercise_button.setMenu(menu)
    layout.addWidget(view.sample_exercise_button)
