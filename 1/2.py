import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QHBoxLayout

class SimpleCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Вычислитель')
        self.resize(500, 50)
        # Поле для ввода, кнопка и поле для вывода
        self.input_expression = QLineEdit(self)
        self.calc_button = QPushButton('Вычислить', self)
        self.result_field = QLineEdit(self)
        # Второе поле для просмотра результата 
        self.result_field.setReadOnly(True)
        # Размещаем элементы горизонтально
        layout = QHBoxLayout()
        layout.addWidget(self.input_expression)
        layout.addWidget(self.calc_button)
        layout.addWidget(self.result_field)
        self.setLayout(layout)
        # Клик по кнопке вызывает функцию вычисления
        self.calc_button.clicked.connect(self.calculate)

    def calculate(self):
        # Получение текста из первого поля
        expression = self.input_expression.text()        
        try:
            result = str(eval(expression))            
            # Записывает результат во второе поле
            self.result_field.setText(result)
        except Exception:
            # Если что-то пошло не так, выводит ошибку
            self.result_field.setText("Ошибка")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimpleCalculator()
    ex.show()
    sys.exit(app.exec())