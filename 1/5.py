import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QCheckBox, QSpinBox,
                             QPushButton, QPlainTextEdit, QVBoxLayout,
                             QHBoxLayout, QLabel)

class RestaurantOrder(QWidget):
    def __init__(self):
        super().__init__()
        # Меню 
        self.menu_data = {
            'Шурпа': 250,
            'Манты': 300,
            'Лагман': 450,
            'Морс': 50,
            'Чай': 70
        }
        # Список для сохранения виджетов
        self.menu_widgets = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Заказ в ресторане')
        self.resize(350, 450)
        # Главный вертикальный слой
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("<b>Меню:</b>"))
        # Генерируем меню в цикле
        for name, price in self.menu_data.items():
            # Для каждого блюда создаем свой горизонтальный слой
            row_layout = QHBoxLayout()            
            cb = QCheckBox(f"{name} ({price} руб.)")            
            sb = QSpinBox()
            sb.setRange(0, 100) # Ограничение по количеству
            sb.setEnabled(False)          
            cb.toggled.connect(lambda checked, spin=sb: self.on_item_toggled(checked, spin))            
            # Размещаем в строке
            row_layout.addWidget(cb)
            row_layout.addStretch()
            row_layout.addWidget(sb)            
            main_layout.addLayout(row_layout)            
            # Сохраняем словарь с данными о блюде в общий список
            self.menu_widgets.append({
                'checkbox': cb,
                'spinbox': sb,
                'name': name,
                'price': price
            })
        # Кнопка для оформления заказа
        self.order_btn = QPushButton("Сформировать чек")
        self.order_btn.clicked.connect(self.generate_receipt)
        main_layout.addWidget(self.order_btn)
        # Поле для вывода чека
        main_layout.addWidget(QLabel("<b>Чек:</b>"))
        self.receipt_field = QPlainTextEdit()
        self.receipt_field.setReadOnly(True) # Чек нельзя редактировать вручную
        main_layout.addWidget(self.receipt_field)
        self.setLayout(main_layout)

    def on_item_toggled(self, checked, spinbox):
        spinbox.setEnabled(checked) # Включаем/отключаем в зависимости от галочки        
        if checked:
            spinbox.setValue(1)
        else:
            # Если галочку сняли, обнуление
            spinbox.setValue(0)

    def generate_receipt(self):
        receipt_text = "=== ВАШ ЗАКАЗ ===\n\n"
        total_sum = 0
        has_items = False
        # Проходимся по списку блюд
        for item in self.menu_widgets:
            # Проверка, стоит ли галочка
            if item['checkbox'].isChecked():
                qty = item['spinbox'].value()                
                if qty > 0:
                    has_items = True
                    # Считаем стоимость блюда каждого типа
                    cost = item['price'] * qty
                    total_sum += cost # Прибавляем к общей сумме
                    # Добавляем строчки в чек
                    receipt_text += f"{item['name']}\n"
                    receipt_text += f"  {item['price']} руб. x {qty} шт. = {cost} руб.\n"

        if not has_items:
            self.receipt_field.setPlainText("Вы ничего не выбрали.")
            return

        receipt_text += "\n=================\n"
        receipt_text += f"ИТОГО К ОПЛАТЕ: {total_sum} руб."        
        # Выводим собранный текст в QPlainTextEdit
        self.receipt_field.setPlainText(receipt_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RestaurantOrder()
    ex.show()
    sys.exit(app.exec())