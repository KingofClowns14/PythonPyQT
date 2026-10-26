import sys
import csv
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt


class OlympiadResults(QMainWindow):
    def __init__(self):
        super().__init__()

        # Определение путей к интерфейсу и базе данных
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '1.ui'
        csv_file_path = current_dir.parent / 'db' / 'rez.csv'

        # Загрузка интерфейса
        uic.loadUi(str(ui_file_path), self)

        # Цвета для призовых мест (золото, серебро, бронза)
        self.PLACE_COLORS = {
            1: QColor(255, 215, 0),
            2: QColor(192, 192, 192),
            3: QColor(205, 127, 50)
        }

        self.data = []
        self.load_data(csv_file_path)

        self.setup_ui()
        self.apply_filter()

    def load_data(self, file_path: Path):
        # Проверка наличия файла данных
        if not file_path.exists():
            return

        # Чтение содержимого с поддержкой основных кодировок
        content = None
        for enc in ['utf-8', 'utf-8-sig', 'windows-1251']:
            try:
                with open(file_path, mode='r', encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if not content:
            return

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            return

        reader = csv.reader(lines, delimiter=',')
        rows = list(reader)

        # Обработка записей таблицы со второй строки (пропуск заголовка)
        for row in rows[1:]:
            if len(row) < 8:
                continue

            user_name = row[1].strip()
            login = row[2].strip()

            # Получение балла из столбца Score (индекс 7)
            try:
                score = int(row[7].strip())
            except ValueError:
                score = 0

            # Извлечение номера школы и класса из шаблона sh-kaluga16-**-##-@
            parts = login.split('-')
            school = parts[2] if len(parts) >= 5 else "Неизвестно"
            cls = parts[3] if len(parts) >= 5 else "Неизвестно"

            self.data.append({
                'login': login,
                'name': user_name,
                'score': score,
                'school': school,
                'class': cls
            })

    def setup_ui(self):
        # Первичная настройка колонок таблицы
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Логин", "ФИО", "Суммарный балл"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Получение уникальных упорядоченных значений школ и классов
        schools = sorted(list(set(item['school'] for item in self.data)))
        classes = sorted(list(set(item['class'] for item in self.data)))

        # Заполнение выпадающих списков
        self.comboSchool.addItem("Все")
        self.comboSchool.addItems(schools)

        self.comboClass.addItem("Все")
        self.comboClass.addItems(classes)

        # Подключение обработчиков изменения фильтров
        self.comboSchool.currentIndexChanged.connect(self.apply_filter)
        self.comboClass.currentIndexChanged.connect(self.apply_filter)

    def apply_filter(self):
        # Получение текущих выбранных значений фильтра
        selected_school = self.comboSchool.currentText()
        selected_class = self.comboClass.currentText()

        # Применение условий фильтрации
        filtered = [
            item for item in self.data
            if (selected_school == "Все" or item['school'] == selected_school)
            and (selected_class == "Все" or item['class'] == selected_class)
        ]

        # Определение трех лучших уникальных результатов (плотное ранжирование)
        unique_scores = sorted(list(set(item['score'] for item in filtered)), reverse=True)
        top_scores = unique_scores[:3]

        # Сопоставление баллов с цветами призеров
        score_to_color = {score: self.PLACE_COLORS[rank] for rank, score in enumerate(top_scores, start=1)}

        # Заполнение строк таблицы
        self.tableWidget.setRowCount(len(filtered))

        for row_idx, item in enumerate(filtered):
            login_item = QTableWidgetItem(item['login'])
            name_item = QTableWidgetItem(item['name'])

            # Запись балла числом для корректной числовой сортировки
            score_item = QTableWidgetItem()
            score_item.setData(Qt.ItemDataRole.DisplayRole, item['score'])

            # Окрашивание ячеек строк призеров
            if item['score'] in score_to_color:
                color = score_to_color[item['score']]
                login_item.setBackground(color)
                name_item.setBackground(color)
                score_item.setBackground(color)

            self.tableWidget.setItem(row_idx, 0, login_item)
            self.tableWidget.setItem(row_idx, 1, name_item)
            self.tableWidget.setItem(row_idx, 2, score_item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OlympiadResults()
    window.show()
    sys.exit(app.exec())