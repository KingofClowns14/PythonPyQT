import sys
import random
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QEvent


class RunawayButtonApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Определение пути к интерфейсу и его загрузка
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '4.ui'
        uic.loadUi(str(ui_file_path), self)

        # Включение отслеживания перемещений мыши без зажатия кнопок
        self.setMouseTracking(True)
        self.centralwidget.setMouseTracking(True)

        # Установка фильтра событий для отслеживания наведения на саму кнопку
        self.btn_run.installEventFilter(self)

    def eventFilter(self, obj, event):
        # Перемещение кнопки при попытке наведения курсора непосредственно на нее
        if obj == self.btn_run and event.type() in (QEvent.Type.Enter, QEvent.Type.MouseMove):
            self.relocate_button()
            return True
        return super().eventFilter(obj, event)

    def mouseMoveEvent(self, event):
        # Проверка расстояния от курсора до границы кнопки
        cursor_pos = event.position().toPoint()
        btn_rect = self.btn_run.geometry()

        # Зона срабатывания (дистанция приближения к кнопке на 40 пикселей)
        detection_zone = btn_rect.adjusted(-40, -40, 40, 40)

        # Перемещение кнопки при попадании курсора в зону приближения
        if detection_zone.contains(cursor_pos):
            self.relocate_button()

        super().mouseMoveEvent(event)

    def relocate_button(self):
        # Расчет допустимой области перемещения внутри границ окна
        max_x = self.centralwidget.width() - self.btn_run.width()
        max_y = self.centralwidget.height() - self.btn_run.height()

        if max_x <= 0 or max_y <= 0:
            return

        # Определение текущей позиции курсора
        cursor_pos = self.centralwidget.mapFromGlobal(self.cursor().pos())

        # Подбор новых координат с исключением появления кнопки под курсором
        for _ in range(50):
            new_x = random.randint(0, max_x)
            new_y = random.randint(0, max_y)

            # Проверка дистанции между новой точкой и текущим положением курсора
            if abs(new_x - cursor_pos.x()) > 80 or abs(new_y - cursor_pos.y()) > 80:
                break

        # Перемещение кнопки на новую позицию
        self.btn_run.move(new_x, new_y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RunawayButtonApp()
    window.show()
    sys.exit(app.exec())