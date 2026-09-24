import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import uic

class TextFlagApp(QWidget):
    def __init__(self):
        super().__init__()       
        # Общая папка 'PythonPyQT'
        root_dir = Path(__file__).resolve().parent.parent        
        # Путь: PythonPyQT -> ui -> 2 -> 1.ui
        ui_file = root_dir / 'ui' / '2' / '1.ui'       
        # Загрузка интерфейса
        uic.loadUi(str(ui_file), self)        
        # Список логических групп кнопок
        self.button_groups = [self.buttonGroup_1, self.buttonGroup_2, self.buttonGroup_3]        
        # Подключение клика кнопки
        self.draw_button.clicked.connect(self.show_result)

    def show_result(self):
        selected_colors = [group.checkedButton().text() for group in self.button_groups]
        self.result_label.setText(", ".join(selected_colors))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextFlagApp()
    ex.show()
    sys.exit(app.exec())