import sys
import random
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QInputDialog, QMainWindow


class FlagGenerator(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '5.ui'
        uic.loadUi(str(ui_file_path), self)

        # Привязка обработчика нажатия кнопки
        self.btn_generate.clicked.connect(self.request_stripes_count)

    def request_stripes_count(self):
        # Запрос количества цветов через диалоговое окно с диапазоном
        count, ok = QInputDialog.getInt(
            self,
            "Количество цветов",
            "Введите количество полос флага (от 1 до 30):",
            value=3,
            min=1,
            max=30,
            step=1
        )

        if ok:
            self.draw_flag(count)

    def draw_flag(self, count):
        # Отрисовка полос флага случайными цветами
        width = 420
        height = 280

        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.white)

        painter = QPainter(pixmap)
        stripe_height = height / count

        for i in range(count):
            # Генерация случайного цвета для текущей полосы
            color = QColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )

            # Вычисление координат полосы
            y_start = int(round(i * stripe_height))
            y_end = int(round((i + 1) * stripe_height))
            h = y_end - y_start

            painter.fillRect(0, y_start, width, h, color)

        painter.end()

        # Отображение полученного флага
        self.lbl_flag.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FlagGenerator()
    window.show()
    sys.exit(app.exec())