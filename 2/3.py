import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6 import uic

class AddressBookApp(QWidget):
    def __init__(self):
        super().__init__()        
        root_dir = Path(__file__).resolve().parent.parent
        ui_file = root_dir / 'ui' / '2' / '3.ui'
        uic.loadUi(str(ui_file), self)
        reg_ex = QRegularExpression(r"^\+?[0-9]*$")
        phone_validator = QRegularExpressionValidator(reg_ex, self.phone_input)
        self.phone_input.setValidator(phone_validator)
        self.add_button.clicked.connect(self.add_contact)

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