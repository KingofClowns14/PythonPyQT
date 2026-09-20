import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QRadioButton, QPushButton, QLabel, QGroupBox, QButtonGroup)
from PyQt6.QtCore import Qt

class TextFlagApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройка заголовка окна
        self.setWindowTitle('Текстовый флаг')        
        # Фиксация размера окна (запрет на изменение размера пользователем)
        self.setFixedSize(650, 500)
        # Инициализация главного вертикального макета
        main_layout = QVBoxLayout()
        # Инициализация горизонтального макета для колонок с цветами
        stripes_layout = QHBoxLayout()
        # Определение списка доступных цветов
        self.colors = ["Белый", "Синий", "Красный", "Зелёный"]        
        # Подготовка списка для хранения групп кнопок
        self.button_groups = []
        # Создание трех колонок для каждой полосы флага
        for i in range(1, 4):
            # Добавление визуальной рамки с заголовком
            group_box = QGroupBox(f"Полоса {i}")
            vbox = QVBoxLayout()            
            # Создание логической группы радиокнопок для текущей полосы
            btn_group = QButtonGroup(self)            
            for j, color in enumerate(self.colors):
                rb = QRadioButton(color)                
                # Установка первого цвета по умолчанию для исключения пустых значений
                if j == 0:
                    rb.setChecked(True)                    
                vbox.addWidget(rb)
                btn_group.addButton(rb)                
            group_box.setLayout(vbox)
            stripes_layout.addWidget(group_box)
            self.button_groups.append(btn_group)
        # Добавление горизонтального макета с полосами в главный макет
        main_layout.addLayout(stripes_layout)
        # Создание и настройка кнопки "Нарисовать"
        self.draw_button = QPushButton("Нарисовать")
        self.draw_button.clicked.connect(self.show_result)
        main_layout.addWidget(self.draw_button)
        # Создание текстовой метки для отображения итогового результата
        self.result_label = QLabel("Выберите цвета и нажмите «Нарисовать»")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)        
        # Настройка шрифта для метки (увеличение размера и жирность)
        font = self.result_label.font()
        font.setPointSize(11)
        font.setBold(True)
        self.result_label.setFont(font)        
        main_layout.addWidget(self.result_label)
        # Применение главного макета к окну приложения
        self.setLayout(main_layout)

    def show_result(self):
        # Извлечение выбранных цветов из каждой группы кнопок
        selected_colors = []
        for group in self.button_groups:
            # Получение текста активной радиокнопки
            selected_color = group.checkedButton().text()
            selected_colors.append(selected_color)
        # Формирование итоговой текстовой строки через запятую
        result_text = ", ".join(selected_colors)        
        # Вывод сформированной строки в текстовую метку на экране
        self.result_label.setText(result_text)


if __name__ == '__main__':
    # Инициализация приложения
    app = QApplication(sys.argv)    
    # Создание и отображение главного окна
    ex = TextFlagApp()
    ex.show()    
    # Запуск основного цикла обработки событий
    sys.exit(app.exec())