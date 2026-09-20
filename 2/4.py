import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

class PseudonymGame(QWidget):
    def __init__(self):
        super().__init__()
        # Хранение текущего количества камней
        self.stones_left = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Игра «Псевдоним»')
        self.resize(450, 350)
        main_layout = QVBoxLayout()
        setup_layout = QHBoxLayout()
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Начальное число камней")
        self.btn_start = QPushButton("Начать новую игру")
        self.btn_start.clicked.connect(self.start_game)        
        setup_layout.addWidget(self.start_input)
        setup_layout.addWidget(self.btn_start)
        self.lbl_stones = QLabel("Камней на столе: -")
        font = self.lbl_stones.font()
        font.setPointSize(14)
        font.setBold(True)
        self.lbl_stones.setFont(font)
        self.lbl_stones.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status = QLabel("Задайте количество камней для старта.")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        game_layout = QHBoxLayout()
        self.take_input = QLineEdit()
        self.take_input.setPlaceholderText("Сколько взять (1-3)?")
        # Отключение поля ввода и кнопки до начала игры
        self.take_input.setEnabled(False)        
        self.btn_take = QPushButton("Взять камни")
        self.btn_take.setEnabled(False)
        self.btn_take.clicked.connect(self.user_turn)
        game_layout.addWidget(self.take_input)
        game_layout.addWidget(self.btn_take)
        main_layout.addLayout(setup_layout)
        main_layout.addWidget(self.lbl_stones)
        main_layout.addWidget(self.lbl_status)
        main_layout.addLayout(game_layout)
        self.setLayout(main_layout)

    # Инициализация новой игры
    def start_game(self):
        start_val = self.start_input.text().strip()        
        # Проверка корректности начального значения (только положительные числа)
        if not start_val.isdigit() or int(start_val) <= 0:
            QMessageBox.warning(self, "Ошибка", "Введите положительное целое число!")
            return
        self.stones_left = int(start_val)
        self.update_ui_state(True)
        self.update_display()
        self.lbl_status.setText("Ваш ход. Возьмите от 1 до 3 камней.")

    # Переключение доступности элементов интерфейса (настройка или процесс игры)
    def update_ui_state(self, is_playing):
        self.start_input.setEnabled(not is_playing)
        self.btn_start.setEnabled(not is_playing)
        self.take_input.setEnabled(is_playing)
        self.btn_take.setEnabled(is_playing)
        if not is_playing:
            self.take_input.clear()

    # Обновление метки с количеством камней на экране
    def update_display(self):
        self.lbl_stones.setText(f"Камней на столе: {self.stones_left}")

    # Обработка хода пользователя
    def user_turn(self):
        take_val = self.take_input.text().strip()
        # Валидация на ввод текста или символов вместо цифр
        if not take_val.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите число (1, 2 или 3).")
            return            
        take_amount = int(take_val)
        # Проверка правил игры (ограничения от 1 до 3 и не больше остатка)
        if take_amount < 1 or take_amount > 3:
            QMessageBox.warning(self, "Ошибка", "Можно взять только от 1 до 3 камней!")
            return
        if take_amount > self.stones_left:
            QMessageBox.warning(self, "Ошибка", "Нельзя взять больше, чем осталось на столе!")
            return
        self.stones_left -= take_amount
        self.take_input.clear()
        self.update_display()
        # Проверка условия победы
        if self.stones_left == 0:
            self.lbl_status.setText("Поздравляем! Вы победили!")
            self.update_ui_state(False)
            return
        self.lbl_status.setText("Ход компьютера...")        
        # Вызов хода искусственного интеллекта
        self.computer_turn()

    # Логика беспроигрышного хода компьютера 
    def computer_turn(self):
        # Вычисление оптимального количества (всегда оставлять противнику кратное 4 число)
        optimal_take = self.stones_left % 4
        # Обработка проигрышной позиции (если уже кратно 4, берется 1 камень для затягивания)
        if optimal_take == 0:
            ai_take = 1
        else:
            ai_take = optimal_take
        # Защита от попытки взять больше камней, чем физически осталось
        ai_take = min(ai_take, self.stones_left)
        self.stones_left -= ai_take
        self.update_display()
        if self.stones_left == 0:
            self.lbl_status.setText(f"Компьютер взял {ai_take} и победил. Вы проиграли.")
            self.update_ui_state(False)
        else:
            self.lbl_status.setText(f"Компьютер взял: {ai_take}. Ваш ход.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PseudonymGame()
    ex.show()
    sys.exit(app.exec())