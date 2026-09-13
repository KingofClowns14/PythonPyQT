import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, 
                             QPushButton, QVBoxLayout, QGridLayout)

# Словарь с азбукой Морзе для латинского алфавита
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..'
}

class MorseTranslator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Азбука Морзе')
        self.resize(400, 200)
        # Основной вертикальный слой
        main_layout = QVBoxLayout()
        # Поле для вывода результата
        self.result_field = QLineEdit(self)
        self.result_field.setReadOnly(True) # Запрет на ручной ввод
        main_layout.addWidget(self.result_field)
        # Слой-сетка для аккуратного размещения кнопок
        grid_layout = QGridLayout()
        # Переменные для отслеживания текущей строки и столбца в сетке
        row = 0
        col = 0
        # Проход циклом по ключам словаря
        for letter in MORSE_CODE_DICT.keys():
            # Создаем кнопку с текстом текущей буквы
            btn = QPushButton(letter, self)            
            # Привязывание клика к одному универсальному обработчику
            btn.clicked.connect(self.add_morse_code)            
            # Добавление кнопки в сетку
            grid_layout.addWidget(btn, row, col)            
            # Сдвиг на один столбец вправо
            col += 1
            # Если в ряду уже 6 кнопок, переходим на новую строку
            if col > 5:
                col = 0
                row += 1
        # Добавляем сетку с кнопками в основной слой
        main_layout.addLayout(grid_layout)        
        # Устанавливаем основной слой для окна
        self.setLayout(main_layout)

    def add_morse_code(self):
        # Определяем какая именно кнопка была нажата
        sender_button = self.sender()        
        # Узнаем какая буква написана на этой кнопке
        letter = sender_button.text()        
        # Получаем код Морзе для этой буквы из словаря
        morse_code = MORSE_CODE_DICT[letter]        
        # Берем текущий текст из поля
        current_text = self.result_field.text()        
        # Добавляем новый код и записываем обратно
        self.result_field.setText(current_text + morse_code + ' ')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MorseTranslator()
    ex.show()
    sys.exit(app.exec())