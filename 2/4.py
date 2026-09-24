import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt6 import uic

class PseudonymGame(QWidget):
    def __init__(self):
        super().__init__()
        self.stones_left = 0        
        root_dir = Path(__file__).resolve().parent.parent
        ui_file = root_dir / 'ui' / '2' / '4.ui'
        uic.loadUi(str(ui_file), self)
        self.btn_start.clicked.connect(self.start_game)
        self.btn_take.clicked.connect(self.user_turn)

    def start_game(self):
        start_val = self.start_input.text().strip()
        if not start_val.isdigit() or int(start_val) <= 0:
            QMessageBox.warning(self, "Ошибка", "Введите положительное целое число!")
            return            
        self.stones_left = int(start_val)
        self.update_ui_state(True)
        self.update_display()
        self.lbl_status.setText("Ваш ход. Возьмите от 1 до 3 камней.")

    def update_ui_state(self, is_playing):
        self.start_input.setEnabled(not is_playing)
        self.btn_start.setEnabled(not is_playing)
        self.take_input.setEnabled(is_playing)
        self.btn_take.setEnabled(is_playing)
        if not is_playing:
            self.take_input.clear()

    def update_display(self):
        self.lbl_stones.setText(f"Камней на столе: {self.stones_left}")

    def user_turn(self):
        take_val = self.take_input.text().strip()
        if not take_val.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите число (1, 2 или 3).")
            return            
        take_amount = int(take_val)
        if take_amount < 1 or take_amount > 3:
            QMessageBox.warning(self, "Ошибка", "Можно взять только от 1 до 3 камней!")
            return
        if take_amount > self.stones_left:
            QMessageBox.warning(self, "Ошибка", "Нельзя взять больше, чем осталось на столе!")
            return
        self.stones_left -= take_amount
        self.take_input.clear()
        self.update_display()
        if self.stones_left == 0:
            self.lbl_status.setText("Поздравляем! Вы победили!")
            self.update_ui_state(False)
            return
        self.lbl_status.setText("Ход компьютера...")
        self.computer_turn()

    def computer_turn(self):
        optimal_take = self.stones_left % 4
        if optimal_take == 0:
            ai_take = 1
        else:
            ai_take = optimal_take
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