import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()        
        # Переменные для хранения состояния
        self.first_operand = None  # Левое число
        self.current_op = None     # Текущая операция (+, -, *, /)
        self.is_new_operand = True # Флаг: вводим ли мы сейчас новое число        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Калькулятор')
        self.resize(300, 400)
        layout = QVBoxLayout()
        # Поле дисплея калькулятора
        self.display = QLineEdit('0')
        self.display.setReadOnly(True)
        # Настраиваем стиль поля
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setStyleSheet("font-size: 32px; padding: 5px;")
        layout.addWidget(self.display)
        # Сетка для кнопок
        grid = QGridLayout()        
        # Описываем кнопки: (Текст, строка, столбец,)
        buttons = [
            ('C', 0, 0, 1, 2), ('±', 0, 2), ('/', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('*', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3)
        ]
        # Создаем кнопки в цикле и расставляем по сетке
        for btn_data in buttons:
            text = btn_data[0]
            btn = QPushButton(text)
            btn.setStyleSheet("font-size: 18px; padding: 15px;")            
            # Привязываем функции в зависимости от типа кнопки
            if text in '0123456789':
                btn.clicked.connect(self.digit_pressed)
            elif text == '.':
                btn.clicked.connect(self.decimal_pressed)
            elif text in '+-*/':
                btn.clicked.connect(self.operator_pressed)
            elif text == '=':
                btn.clicked.connect(self.equals_pressed)
            elif text == 'C':
                btn.clicked.connect(self.clear_pressed)
            elif text == '±':
                btn.clicked.connect(self.negate_pressed)
            # Если для кнопки указаны параметры объединения ячеек (например, для '0' и 'C')
            if len(btn_data) == 5:
                grid.addWidget(btn, btn_data[1], btn_data[2], btn_data[3], btn_data[4])
            else:
                grid.addWidget(btn, btn_data[1], btn_data[2])
        layout.addLayout(grid)
        self.setLayout(layout)

    def digit_pressed(self):
        btn = self.sender()
        digit = btn.text()        
        # Если на экране ошибка, сбрасываем всё перед вводом новой цифры
        if self.display.text() == 'Ошибка':
            self.clear_pressed()
        if self.is_new_operand:
            self.display.setText(digit)
            self.is_new_operand = False
        else:
            if self.display.text() == '0':
                self.display.setText(digit)
            else:
                self.display.setText(self.display.text() + digit)

    def decimal_pressed(self):
        if self.display.text() == 'Ошибка':
            self.clear_pressed()            
        if self.is_new_operand:
            self.display.setText('0.')
            self.is_new_operand = False
        elif '.' not in self.display.text():
            self.display.setText(self.display.text() + '.')

    def negate_pressed(self):
        if self.display.text() == 'Ошибка':
            return            
        val = float(self.display.text())
        val = -val        
        # Убираем .0, если это целое число
        if val.is_integer():
            val = int(val)
        self.display.setText(str(val))

    def operator_pressed(self):
        btn = self.sender()
        op = btn.text()        
        if self.display.text() == 'Ошибка':
            return
        # Если уже была сохранена предыдущая операция, последовательно вычисляем её
        if self.first_operand is not None and not self.is_new_operand:
            self.calculate()        
        # Если при вычислении произошла ошибка прерываем процесс
        if self.display.text() == 'Ошибка':
            return
        # Запоминаем текущее число и нажатую операцию
        self.first_operand = float(self.display.text())
        self.current_op = op
        self.is_new_operand = True

    def equals_pressed(self):
        if self.display.text() == 'Ошибка' or self.current_op is None:
            return        
        self.calculate()        
        # Сбрасываем операторы после вывода результата
        self.first_operand = None
        self.current_op = None
        self.is_new_operand = True

    def clear_pressed(self):
        self.first_operand = None
        self.current_op = None
        self.is_new_operand = True
        self.display.setText('0')

    def calculate(self):
        right_operand = float(self.display.text())
        left_operand = self.first_operand
        if self.current_op == '+':
            res = left_operand + right_operand
        elif self.current_op == '-':
            res = left_operand - right_operand
        elif self.current_op == '*':
            res = left_operand * right_operand
        elif self.current_op == '/':
            # Защита от деления на ноль
            if right_operand == 0:
                self.display.setText('Ошибка')
                return
            res = left_operand / right_operand
        if res.is_integer():
            res = int(res)            
        self.display.setText(str(res))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())