import sys
import random
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QColor, QPolygonF, QCursor
from PyQt6.QtCore import Qt, QPointF


class ShapeDrawer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Определение пути к интерфейсу и его загрузка
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '3.ui'
        uic.loadUi(str(ui_file_path), self)

        # Установка произвольного начального размера формы
        init_width = random.randint(400, 800)
        init_height = random.randint(350, 650)
        self.resize(init_width, init_height)

        # Генерация случайной начальной фигуры в центре экрана
        initial_type = random.choice(['circle', 'square', 'triangle'])
        initial_size = random.randint(30, 120)
        self.current_shape = (
            initial_type,
            init_width / 2,
            init_height / 2,
            initial_size,
            self.get_random_color()
        )

    def get_random_color(self) -> QColor:
        # Генерация случайного цвета
        return QColor(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    def mousePressEvent(self, event):
        # Определение параметров и отрисовка фигуры по кнопке мыши
        pos = event.position()
        x, y = pos.x(), pos.y()
        size = random.randint(20, 120)
        color = self.get_random_color()

        if event.button() == Qt.MouseButton.LeftButton:
            # Круг по нажатию левой кнопки мыши
            self.current_shape = ('circle', x, y, size, color)
            self.update()

        elif event.button() == Qt.MouseButton.RightButton:
            # Квадрат по нажатию правой кнопки мыши
            self.current_shape = ('square', x, y, size, color)
            self.update()

    def keyPressEvent(self, event):
        # Обработка нажатия клавиши Пробел
        if event.key() == Qt.Key.Key_Space:
            # Определение координат курсора относительно окна приложения
            local_pos = self.mapFromGlobal(QCursor.pos())
            x, y = local_pos.x(), local_pos.y()
            size = random.randint(20, 120)
            color = self.get_random_color()

            # Треугольник в позиции курсора
            self.current_shape = ('triangle', x, y, size, color)
            self.update()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        # Отрисовка активной фигуры на поверхности окна
        super().paintEvent(event)

        if not self.current_shape:
            return

        shape_type, x, y, size, color = self.current_shape
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        half_size = size / 2

        if shape_type == 'circle':
            # Рисование круга с центром в заданной точке
            painter.drawEllipse(QPointF(x, y), half_size, half_size)

        elif shape_type == 'square':
            # Рисование квадрата с центром в заданной точке
            painter.drawRect(
                int(x - half_size),
                int(y - half_size),
                int(size),
                int(size)
            )

        elif shape_type == 'triangle':
            # Расчет вершин и рисование треугольника
            p1 = QPointF(x, y - half_size)
            p2 = QPointF(x - half_size, y + half_size)
            p3 = QPointF(x + half_size, y + half_size)

            polygon = QPolygonF([p1, p2, p3])
            painter.drawPolygon(polygon)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShapeDrawer()
    window.show()
    sys.exit(app.exec())