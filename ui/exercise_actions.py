"""Bilingual exercise file actions shared by Chapter 1 design tools."""
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox, QPushButton
from logic_exercise import read_exercise, write_exercise


def add_exercise_actions(view, layout, kind):
    """Only explicit user actions read/write files; validate before replacing."""
    def t(en, fa):
        return fa if view.fa else en

    file_filter = t("Mano exercise (*.mano-exercise.json)", "تمرین مانو (*.mano-exercise.json)") + ";;JSON (*.json)"

    def open_file():
        name, _ = QFileDialog.getOpenFileName(view, t("Open exercise", "باز کردن تمرین"), "", file_filter)
        if not name:
            return
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
                                               kind+".mano-exercise.json", file_filter)
        if not name:
            return
        path = Path(name)
        if not path.suffix:
            path = path.with_suffix(".mano-exercise.json")
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
