import sys
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QColorDialog, QMainWindow


class SmileyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '6.ui'
        uic.loadUi(str(ui_file_path), self)

        # Начальные параметры смайлика
        self.face_color = QColor(255, 220, 50)

        # Привязка обработчиков
        self.btn_color.clicked.connect(self.select_color)
        self.slider_scale.valueChanged.connect(self.draw_smiley)

        # Отрисовка смайлика при старте
        self.draw_smiley()

    def select_color(self):
        # Выбор цвета через диалоговое окно
        color = QColorDialog.getColor(self.face_color, self, "Выберите цвет смайлика")
        if color.isValid():
            self.face_color = color
            self.draw_smiley()

    def draw_smiley(self):
        # Отрисовка смайлика с учетом масштаба и цвета
        canvas_w = 450
        canvas_h = 450
        pixmap = QPixmap(canvas_w, canvas_h)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Расчет размеров по коэффициенту масштабирования
        scale = self.slider_scale.value() / 100.0
        base_radius = 180 * scale
        center_x = canvas_w / 2
        center_y = canvas_h / 2

        # Отрисовка основы головы
        pen = QPen(Qt.GlobalColor.black, max(2, int(3 * scale)))
        painter.setPen(pen)
        painter.setBrush(QBrush(self.face_color))
        painter.drawEllipse(
            int(center_x - base_radius / 2),
            int(center_y - base_radius / 2),
            int(base_radius),
            int(base_radius)
        )

        # Отрисовка глаз
        eye_w = int(base_radius * 0.12)
        eye_h = int(base_radius * 0.18)
        eye_y = int(center_y - base_radius * 0.18)
        left_eye_x = int(center_x - base_radius * 0.22)
        right_eye_x = int(center_x + base_radius * 0.1)

        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(left_eye_x, eye_y, eye_w, eye_h)
        painter.drawEllipse(right_eye_x, eye_y, eye_w, eye_h)

        # Отрисовка улыбки
        mouth_w = int(base_radius * 0.55)
        mouth_h = int(base_radius * 0.35)
        mouth_x = int(center_x - mouth_w / 2)
        mouth_y = int(center_y - mouth_h * 0.1)

        smile_pen = QPen(Qt.GlobalColor.black, max(2, int(4 * scale)))
        smile_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(smile_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(mouth_x, mouth_y, mouth_w, mouth_h, 205 * 16, 130 * 16)

        painter.end()

        # Отображение смайлика в интерфейсе
        self.lbl_canvas.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SmileyApp()
    window.show()
    sys.exit(app.exec())