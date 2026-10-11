import sys
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox


class NumberStatsApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Определение пути к файлу интерфейса и его загрузка
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '1.ui'
        uic.loadUi(str(ui_file_path), self)

        # Инициализация переменных состояния
        self.max_val = None
        self.min_val = None
        self.avg_val = None

        self.btn_save.setEnabled(False)

        # Подключение сигналов к кнопкам
        self.btn_load.clicked.connect(self.load_data)
        self.btn_save.clicked.connect(self.save_data)

    def load_data(self):
        # Выбор и чтение входного файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите текстовый файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Разбиение строки по пробельным символам
            tokens = content.split()

            if not tokens:
                raise ValueError("Файл пуст или содержит только пробелы.")

            # Парсинг целых чисел и вычисление статистики
            numbers = [int(token) for token in tokens]

            self.max_val = max(numbers)
            self.min_val = min(numbers)
            self.avg_val = sum(numbers) / len(numbers)

            # Вывод результатов в форму
            self.line_max.setText(str(self.max_val))
            self.line_min.setText(str(self.min_val))
            self.line_avg.setText(f"{self.avg_val:.2f}")

            self.btn_save.setEnabled(True)

        except ValueError:
            self.clear_fields()
            QMessageBox.critical(
                self,
                "Ошибка формата данных",
                "Файл содержит некорректные данные!\n"
                "Разрешены только целые числа, разделенные пробельными символами."
            )
        except Exception as e:
            self.clear_fields()
            QMessageBox.critical(
                self,
                "Ошибка чтения",
                f"Не удалось открыть или прочитать файл:\n{e}"
            )

    def save_data(self):
        # Сохранение результатов в выбранный файл
        if self.max_val is None:
            QMessageBox.warning(self, "Предупреждение", "Данные для сохранения отсутствуют.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить результаты",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Максимальное значение: {self.max_val}\n")
                f.write(f"Минимальное значение: {self.min_val}\n")
                f.write(f"Среднее значение: {self.avg_val:.2f}\n")

            QMessageBox.information(self, "Успех", "Данные успешно сохранены.")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка записи",
                f"Не удалось записать файл:\n{e}"
            )

    def clear_fields(self):
        # Очистка полей и сброс состояния
        self.max_val = None
        self.min_val = None
        self.avg_val = None
        self.line_max.clear()
        self.line_min.clear()
        self.line_avg.clear()
        self.btn_save.setEnabled(False)


if __name__ == '__main__':
    # Запуск приложения
    app = QApplication(sys.argv)
    window = NumberStatsApp()
    window.show()
    sys.exit(app.exec())