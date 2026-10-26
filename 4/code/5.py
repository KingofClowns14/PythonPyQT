import sys
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class UfoGame(QMainWindow):
    def __init__(self):
        super().__init__()

        # Определение базовой директории для обычного запуска и собранного бинарника
        if hasattr(sys, '_MEIPASS'):
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).resolve().parent.parent

        ui_file_path = base_dir / 'ui' / '5.ui'
        image_path = base_dir / 'img' / 'ufo.png'

        # Загрузка интерфейса
        uic.loadUi(str(ui_file_path), self)

        # Установка изображения в виджет
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            self.ufo.setPixmap(pixmap)
            self.ufo.setScaledContents(True)

        # Константа шага перемещения
        self.STEP = 20

        # Активация перехвата событий клавиатуры
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def keyPressEvent(self, event):
        # Получение текущих координат и габаритов объекта
        x = self.ufo.x()
        y = self.ufo.y()
        w = self.ufo.width()
        h = self.ufo.height()

        # Определение границ рабочей области окна
        area_width = self.centralWidget().width()
        area_height = self.centralWidget().height()

        key = event.key()

        # Смещение координат в зависимости от направления
        if key == Qt.Key.Key_Left:
            x -= self.STEP
        elif key == Qt.Key.Key_Right:
            x += self.STEP
        elif key == Qt.Key.Key_Up:
            y -= self.STEP
        elif key == Qt.Key.Key_Down:
            y += self.STEP
        else:
            super().keyPressEvent(event)
            return

        # Перенос объекта на противоположную сторону при выходе за границы формы
        if x + w <= 0:
            x = area_width
        elif x >= area_width:
            x = -w

        if y + h <= 0:
            y = area_height
        elif y >= area_height:
            y = -h

        # Установка новых координат
        self.ufo.move(x, y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UfoGame()
    window.show()
    sys.exit(app.exec())