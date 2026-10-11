import sys
import math
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox


class LSystemApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '8.ui'
        uic.loadUi(str(ui_file_path), self)

        # Параметры L-системы
        self.system_name = ""
        self.angle_divisor = 1
        self.axiom = ""
        self.rules = {}

        # Привязка слайдера
        self.slider_step.valueChanged.connect(self.on_step_changed)

        # Вызов диалога выбора файла конфигурации
        self.load_definition_file()

    def load_definition_file(self):
        # Открытие и чтение файла с описанием L-системы
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл описания L-системы",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if not file_path:
            sys.exit(0)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            # Парсинг строк файла
            self.system_name = lines[0]
            self.angle_divisor = int(lines[1])
            self.axiom = lines[2]

            # Чтение теорем подстановки
            self.rules = {}
            for line in lines[3:]:
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    self.rules[parts[0]] = parts[1]
                elif len(parts) == 1:
                    self.rules[parts[0]] = ""

            self.lbl_title.setText(self.system_name)
            self.setWindowTitle(f"L-система — {self.system_name}")

            # Отрисовка первого шага по умолчанию
            self.slider_step.setValue(1)
            self.draw_system(1)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл L-системы:\n{e}")
            sys.exit(1)

    def on_step_changed(self, step):
        # Обработка изменения шага слайдером
        self.lbl_step_val.setText(str(step))
        self.draw_system(step)

    def generate_instructions(self, step):
        # Генерация последовательности символов для заданного шага
        current = self.axiom
        for _ in range(step):
            next_chars = [self.rules.get(ch, ch) for ch in current]
            current = "".join(next_chars)
        return current

    def draw_system(self, step):
        # Построение и масштабирование графики L-системы
        instructions = self.generate_instructions(step)
        angle_rad = 2 * math.pi / self.angle_divisor

        # Моделирование координат отрезков черепашьей графики
        segments = []
        x, y = 0.0, 0.0
        angle = 0.0
        stack = []

        for ch in instructions:
            if ch == '+':
                angle += angle_rad
            elif ch == '-':
                angle -= angle_rad
            elif ch == '[':
                stack.append((x, y, angle))
            elif ch == ']':
                if stack:
                    x, y, angle = stack.pop()
            else:
                nx = x + math.cos(angle)
                ny = y + math.sin(angle)
                segments.append(((x, y), (nx, ny)))
                x, y = nx, ny

        if not segments:
            return

        # Поиск габаритов для центрирования и масштабирования
        all_xs = [pt[0] for seg in segments for pt in seg]
        all_ys = [pt[1] for seg in segments for pt in seg]
        min_x, max_x = min(all_xs), max(all_xs)
        min_y, max_y = min(all_ys), max(all_ys)

        span_x = max(max_x - min_x, 1e-6)
        span_y = max(max_y - min_y, 1e-6)

        w = self.lbl_canvas.width()
        h = self.lbl_canvas.height()
        padding = 30

        scale = min((w - 2 * padding) / span_x, (h - 2 * padding) / span_y)
        offset_x = (w - span_x * scale) / 2 - min_x * scale
        offset_y = (h - span_y * scale) / 2 - min_y * scale

        # Отрисовка на холсте
        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.GlobalColor.white)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(30, 120, 200), 2))

        for (x1, y1), (x2, y2) in segments:
            px1 = x1 * scale + offset_x
            py1 = y1 * scale + offset_y
            px2 = x2 * scale + offset_x
            py2 = y2 * scale + offset_y
            painter.drawLine(QPointF(px1, py1), QPointF(px2, py2))

        painter.end()
        self.lbl_canvas.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LSystemApp()
    window.show()
    sys.exit(app.exec())