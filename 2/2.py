import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QCalendarWidget, QTimeEdit, QListWidget, 
                             QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import QTime, Qt

class PlannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройка заголовка и начального размера окна
        self.setWindowTitle('Ежедневник')
        self.resize(900, 650)
        main_layout = QHBoxLayout()
        # Создание левой панели для элементов управления (календарь, время, ввод)
        left_panel = QVBoxLayout()
        # Добавление виджета календаря
        self.calendar = QCalendarWidget()
        left_panel.addWidget(self.calendar)
        # Создание горизонтального макета для выбора времени
        time_layout = QHBoxLayout()
        time_label = QLabel("Время:")        
        # Добавление виджета выбора времени
        self.time_edit = QTimeEdit()
        # Установка текущего времени по умолчанию
        self.time_edit.setTime(QTime.currentTime())        
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        left_panel.addLayout(time_layout)
        # Добавление поля для ввода названия события
        self.event_input = QLineEdit()
        self.event_input.setPlaceholderText("Введите название события...")
        left_panel.addWidget(self.event_input)
        # Добавление кнопки "Добавить"
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_event)
        left_panel.addWidget(self.add_button)        
        # Выравнивание элементов левой панели по верхнему краю
        left_panel.addStretch()
        # Создание правой панели для отображения событий
        self.event_list = QListWidget()
        # Добавление панелей в главный макет
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.event_list, 1)
        # Применение главного макета к окну приложения
        self.setLayout(main_layout)

    def add_event(self):
        # Получение текста из поля ввода с удалением лишних пробелов по краям
        event_name = self.event_input.text().strip()
        # Проверка на пустое поле ввода
        if not event_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название события!")
            return
        # Извлечение выбранной даты в формате ГГГГ-ММ-ДД
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")        
        # Извлечение выбранного времени в формате ЧЧ:ММ
        selected_time = self.time_edit.time().toString("HH:mm")
        # Формирование итоговой строки для добавления в список
        # Формат 'ГГГГ-ММ-ДД ЧЧ:ММ' гарантирует правильную алфавитную сортировку
        event_string = f"{selected_date} {selected_time} — {event_name}"
        # Добавление сформированной строки в виджет списка
        self.event_list.addItem(event_string)
        # Сортировка элементов списка по возрастанию
        self.event_list.sortItems(Qt.SortOrder.AscendingOrder)
        # Очистка поля ввода для следующего события
        self.event_input.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)    
    planner = PlannerApp()
    planner.show()
    sys.exit(app.exec())