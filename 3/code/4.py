import sys
from pathlib import Path
from PIL import Image
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox


class TransparencyEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка разметки интерфейса
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '4.ui'
        uic.loadUi(str(ui_file_path), self)

        self.original_image = None

        # Привязка обработчиков событий
        self.btn_open.clicked.connect(self.open_image)
        self.slider_alpha.valueChanged.connect(self.on_slider_changed)

    def open_image(self):
        # Выбор и открытие графического файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.webp);;Все файлы (*.*)"
        )

        if not file_path:
            return

        try:
            # Приведение к формату RGBA для работы с альфа-каналом
            self.original_image = Image.open(file_path).convert('RGBA')
            self.slider_alpha.setValue(255)
            self.update_image_display()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение:\n{e}")

    def on_slider_changed(self, value):
        # Обновление текстового значения и перерисовка
        self.lbl_alpha_val.setText(str(value))
        self.update_image_display()

    def update_image_display(self):
        # Пересчет альфа-канала и вывод на экран
        if self.original_image is None:
            return

        alpha_factor = self.slider_alpha.value() / 255.0

        # Разделение каналов и масштабирование прозрачности
        r, g, b, a = self.original_image.split()
        modified_alpha = a.point(lambda p: int(p * alpha_factor))
        result_img = Image.merge('RGBA', (r, g, b, modified_alpha))

        # Преобразование в QPixmap
        data = result_img.tobytes("raw", "RGBA")
        q_img = QImage(
            data,
            result_img.width,
            result_img.height,
            result_img.width * 4,
            QImage.Format.Format_RGBA8888
        )
        pixmap = QPixmap.fromImage(q_img)

        # Масштабирование под размер метки
        scaled_pixmap = pixmap.scaled(
            self.lbl_image.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_image.setPixmap(scaled_pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransparencyEditor()
    window.show()
    sys.exit(app.exec())