import sys
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '2.ui'
        uic.loadUi(str(ui_file_path), self)

        # Путь к текущему открытому файлу
        self.current_file_path = None

        # Подключение обработчиков кнопок
        self.btn_create.clicked.connect(self.create_file)
        self.btn_open.clicked.connect(self.open_file)
        self.btn_save.clicked.connect(self.save_file)

    def create_file(self):
        # Создание нового документа и сброс пути
        self.text_browser.clear()
        self.current_file_path = None
        self.setWindowTitle("Текстовый редактор — Новый файл")

    def open_file(self):
        # Открытие существующего файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            self.text_browser.setPlainText(content)
            self.current_file_path = file_path
            self.setWindowTitle(f"Текстовый редактор — {Path(file_path).name}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка открытия",
                f"Не удалось открыть файл:\n{e}"
            )

    def save_file(self):
        # Сохранение текста в текущий или новый файл
        if not self.current_file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить файл",
                "",
                "Текстовые файлы (*.txt);;Все файлы (*)"
            )
            if not file_path:
                return
            self.current_file_path = file_path

        try:
            content = self.text_browser.toPlainText()
            with open(self.current_file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            self.setWindowTitle(f"Текстовый редактор — {Path(self.current_file_path).name}")
            QMessageBox.information(self, "Успех", "Файл успешно сохранен.")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка сохранения",
                f"Не удалось сохранить файл:\n{e}"
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextEditor()
    window.show()
    sys.exit(app.exec())