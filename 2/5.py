import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic

class PlagiarismCheckerApp(QMainWindow):
    def __init__(self):
        super().__init__()        
        root_dir = Path(__file__).resolve().parent.parent
        ui_file = root_dir / 'ui' / '2' / '5.ui'
        uic.loadUi(str(ui_file), self)
        self.statusBar().showMessage("Ожидание текстов для проверки...")
        self.btn_check.clicked.connect(self.check_plagiarism)

    def check_plagiarism(self):
        text1 = self.text1_edit.toPlainText().strip()
        text2 = self.text2_edit.toPlainText().strip()
        threshold = self.spin_threshold.value()
        if not text1 or not text2:
            self.statusBar().setStyleSheet("color: red;")
            self.statusBar().showMessage("Ошибка: оба поля должны быть заполнены!")
            return
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        common_words = words1.intersection(words2)
        all_words = words1.union(words2)
        if not all_words:
            similarity = 0.0
        else:
            similarity = (len(common_words) / len(all_words)) * 100

        if similarity >= threshold:
            self.statusBar().setStyleSheet("color: red; font-weight: bold;")
            self.statusBar().showMessage(f"Плагиат обнаружен! Схожесть: {similarity:.1f}% (Порог: {threshold}%)")
        else:
            self.statusBar().setStyleSheet("color: green; font-weight: bold;")
            self.statusBar().showMessage(f"Текст оригинален. Схожесть: {similarity:.1f}% (Порог: {threshold}%)")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PlagiarismCheckerApp()
    ex.show()
    sys.exit(app.exec())