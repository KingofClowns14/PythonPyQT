import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QMessageBox)
# Импорт классов для создания регулярных выражений и валидатора
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

class AddressBookApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Записная книжка')
        self.resize(600, 500)
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя контакта")        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Номер телефона")        
        # Ограничение максимального количества символов
        self.phone_input.setMaxLength(12)        
        # Создание регулярного выражения: опциональный '+' в начале (^\+?) и только цифры ([0-9]*)
        reg_ex = QRegularExpression(r"^\+?[0-9]*$")
        # Создание валидатора на основе выражения и применение его к полю ввода
        phone_validator = QRegularExpressionValidator(reg_ex, self.phone_input)
        self.phone_input.setValidator(phone_validator)        
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.phone_input)
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_contact)
        self.contact_list = QListWidget()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.add_button)
        main_layout.addWidget(self.contact_list)
        self.setLayout(main_layout)

    def add_contact(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        if not name or not phone:
            QMessageBox.warning(self, "Ошибка", "Заполните оба поля!")
            return
        contact_entry = f"{name} — {phone}"
        self.contact_list.addItem(contact_entry)
        self.name_input.clear()
        self.phone_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AddressBookApp()
    ex.show()
    sys.exit(app.exec())