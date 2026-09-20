import sys
# Импорт QMainWindow (базовый класс окна со строкой состояния), QDoubleSpinBox (ввод дробных чисел) и QTextEdit (многострочный текст)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                             QDoubleSpinBox)

class PlagiarismCheckerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Антиплагиат')
        self.resize(700, 500)
        # QMainWindow требует создания и установки центрального виджета, в который помещаются макеты
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        settings_layout = QHBoxLayout()
        lbl_threshold = QLabel("Порог срабатывания (%):")        
        # Создание виджета для ввода дробных чисел (порога)
        self.spin_threshold = QDoubleSpinBox()
        # Установка диапазона от 0 до 100 процентов
        self.spin_threshold.setRange(0.0, 100.0)
        # Установка значения по умолчанию
        self.spin_threshold.setValue(70.0)
        settings_layout.addWidget(lbl_threshold)
        settings_layout.addWidget(self.spin_threshold)
        settings_layout.addStretch()
        texts_layout = QHBoxLayout()        
        # Создание виджетов для многострочного ввода текста
        self.text1_edit = QTextEdit()
        self.text1_edit.setPlaceholderText("Вставьте первый текст сюда...")        
        self.text2_edit = QTextEdit()
        self.text2_edit.setPlaceholderText("Вставьте второй текст сюда...")
        texts_layout.addWidget(self.text1_edit)
        texts_layout.addWidget(self.text2_edit)
        self.btn_check = QPushButton("Проверить")
        self.btn_check.clicked.connect(self.check_plagiarism)
        main_layout.addLayout(settings_layout)
        main_layout.addLayout(texts_layout)
        main_layout.addWidget(self.btn_check)
        central_widget.setLayout(main_layout)
        # Вывод начального сообщения во встроенную строку состояния (StatusBar)
        self.statusBar().showMessage("Ожидание текстов для проверки...")

    def check_plagiarism(self):
        # Получение текста из многострочных полей (toPlainText вместо text)
        text1 = self.text1_edit.toPlainText().strip()
        text2 = self.text2_edit.toPlainText().strip()
        threshold = self.spin_threshold.value()
        if not text1 or not text2:
            self.statusBar().setStyleSheet("color: red;")
            self.statusBar().showMessage("Ошибка: оба поля должны быть заполнены!")
            return
        # Пользовательский алгоритм сравнения (Индекс Жаккара по словам)
        # Разбиение текстов на множества уникальных слов в нижнем регистре
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        # Нахождение общих слов (пересечение множеств)
        common_words = words1.intersection(words2)
        # Нахождение общего пула слов (объединение множеств)
        all_words = words1.union(words2)
        # Расчет процента схожести
        if not all_words:
            similarity = 0.0
        else:
            similarity = (len(common_words) / len(all_words)) * 100
        # Изменение цвета текста в StatusBar через таблицы стилей (CSS) и вывод результата
        if similarity >= threshold:
            self.statusBar().setStyleSheet("color: red; font-weight: bold;")
            self.statusBar().showMessage(f"Плагиат обнаружен! Схожесть: {similarity:.1f}% (Порог: {threshold}%)")
        else:
            self.statusBar().setStyleSheet("color: green; font-weight: bold;")
            self.statusBar().showMessage(f"Текст оригинален. Схожесть: {similarity:.1f}% (Порог: {threshold}%)")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PlagiarismCheckerApp()
    ex.show()
    sys.exit(app.exec())