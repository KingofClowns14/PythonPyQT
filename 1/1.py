import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QHBoxLayout

class WordTosser(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # Переменная для отслеживания направления. 
        # True - слева направо (->), False - справа налево (<-)
        self.direction_right = True 

    def initUI(self):
        self.setWindowTitle('Перекидыватель слов')
        self.resize(400, 50) # Начальный размер окна
        # Элементы управления
        self.input1 = QLineEdit(self)
        self.input2 = QLineEdit(self)
        self.button = QPushButton('->', self)
        # Размещение элементов горизонтально
        layout = QHBoxLayout()
        layout.addWidget(self.input1)
        layout.addWidget(self.button)
        layout.addWidget(self.input2)
        self.setLayout(layout)
        # Привязывание кнопки к методу
        self.button.clicked.connect(self.toss_word)

    def toss_word(self):
        # Если направление слева направо
        if self.direction_right:
            # Берем текст из левого поля
            text = self.input1.text()
            # Вставляем в правое
            self.input2.setText(text)
            # Очищаем левое
            self.input1.clear()
            # Меняем стрелку
            self.button.setText('<-')
            # Меняем направление для следующего клика
            self.direction_right = False
        # Если направление справа налево
        else:
            text = self.input2.text()
            self.input1.setText(text)
            self.input2.clear()
            self.button.setText('->')
            self.direction_right = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WordTosser()
    ex.show()
    sys.exit(app.exec())