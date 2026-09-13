import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QCheckBox, 
                             QLineEdit, QPushButton, QLabel, 
                             QVBoxLayout, QHBoxLayout)

class WidgetToggler(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Управление видимостью виджетов')
        self.resize(400, 150)
        # Создание трёх произвольных виджета
        self.line_edit = QLineEdit("Какой-то текст")
        self.button = QPushButton("Нажми меня")
        self.label = QLabel("Просто текстовая метка")
        # Создание трёх чекбокса
        self.cb_line_edit = QCheckBox("Поле ввода")
        self.cb_line_edit.setChecked(True)        
        self.cb_button = QCheckBox("Кнопка")
        self.cb_button.setChecked(True)        
        self.cb_label = QCheckBox("Метка")
        self.cb_label.setChecked(True)
        # Словарь, который связывает чекбоксы и виджеты
        self.widgets_map = {
            self.cb_line_edit: self.line_edit,
            self.cb_button: self.button,
            self.cb_label: self.label
        }
        # Основной вертикальный слой
        main_layout = QVBoxLayout()
        # Размещаем элементы и привязываем 1 сигнал
        for checkbox, widget in self.widgets_map.items():
            # Создаем горизонтальный слой для пары чекбокс - виджет
            row_layout = QHBoxLayout()
            row_layout.addWidget(checkbox)
            row_layout.addWidget(widget)            
            # Добавляем строку в главный слой
            main_layout.addLayout(row_layout)
            checkbox.toggled.connect(self.universal_handler)
        self.setLayout(main_layout)

    # Универсальный обработчик
    def universal_handler(self, is_checked):
        # self.sender() возвращает чекбокс который вызвал эту функцию
        sender_checkbox = self.sender()        
        # Находим в словаре виджет который привязан к этому чекбоксу
        target_widget = self.widgets_map.get(sender_checkbox)        
        if target_widget:
            target_widget.setVisible(is_checked)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WidgetToggler()
    ex.show()
    sys.exit(app.exec())