import sys
from pathlib import Path
from PIL import Image
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox


class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '3.ui'
        uic.loadUi(str(ui_file_path), self)

        # Состояния преобразований
        self.original_image = None
        self.current_channel = 'ALL'
        self.angle = 0

        # Привязка обработчиков цветовых каналов
        self.btn_r.clicked.connect(lambda: self.set_channel('R'))
        self.btn_g.clicked.connect(lambda: self.set_channel('G'))
        self.btn_b.clicked.connect(lambda: self.set_channel('B'))
        self.btn_all.clicked.connect(lambda: self.set_channel('ALL'))

        # Привязка обработчиков поворотов
        self.btn_rotate_left.clicked.connect(lambda: self.rotate_image(90))
        self.btn_rotate_right.clicked.connect(lambda: self.rotate_image(-90))

        # Вызов диалога выбора изображения при запуске
        self.load_initial_image()

    def load_initial_image(self):
        # Открытие диалога выбора графического файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.webp);;Все файлы (*.*)"
        )

        if not file_path:
            sys.exit(0)

        try:
            # Приведение изображения к RGB-формату
            self.original_image = Image.open(file_path).convert('RGB')
            self.update_view()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл как изображение:\n{e}")
            sys.exit(1)

    def set_channel(self, channel):
        # Переключение активного цветового канала
        self.current_channel = channel
        self.update_view()

    def rotate_image(self, delta_angle):
        # Изменение угла поворота с нормализацией
        self.angle = (self.angle + delta_angle) % 360
        self.update_view()

    def update_view(self):
        # Применение преобразований к изображению
        if self.original_image is None:
            return

        img = self.original_image.copy()

        # Фильтрация по цветовым каналам
        if self.current_channel != 'ALL':
            r, g, b = img.split()
            black = Image.new('L', img.size, 0)
            if self.current_channel == 'R':
                img = Image.merge('RGB', (r, black, black))
            elif self.current_channel == 'G':
                img = Image.merge('RGB', (black, g, black))
            elif self.current_channel == 'B':
                img = Image.merge('RGB', (black, black, b))

        # Применение угла поворота
        if self.angle != 0:
            img = img.rotate(self.angle, expand=True)

        # Конвертация PIL Image в QPixmap
        data = img.tobytes("raw", "RGB")
        q_img = QImage(data, img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        # Отображение с масштабированием под размер виджета
        target_size = self.lbl_image.size()
        scaled_pixmap = pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_image.setPixmap(scaled_pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageEditor()
    window.show()
    sys.exit(app.exec())