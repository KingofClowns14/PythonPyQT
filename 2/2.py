import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt6.QtCore import QTime, Qt
from PyQt6 import uic

class PlannerApp(QWidget):
    def __init__(self):
        super().__init__()        
        root_dir = Path(__file__).resolve().parent.parent
        ui_file = root_dir / 'ui' / '2' / '2.ui'     
        uic.loadUi(str(ui_file), self)
        self.time_edit.setTime(QTime.currentTime())
        self.add_button.clicked.connect(self.add_event)

    def add_event(self):
        event_name = self.event_input.text().strip()
        if not event_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название события!")
            return
        date_obj = self.calendar.selectedDate()
        if date_obj.year() < 1900 or date_obj.year() > 2100:
            QMessageBox.warning(self, "Ошибка", "Выбран некорректный год!")
            return
        selected_date = date_obj.toString("yyyy-MM-dd")
        selected_time = self.time_edit.time().toString("HH:mm")
        event_string = f"{selected_date} {selected_time} — {event_name}"
        self.event_list.addItem(event_string)
        self.event_list.sortItems(Qt.SortOrder.AscendingOrder)
        self.event_input.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    planner = PlannerApp()
    planner.show()
    sys.exit(app.exec())