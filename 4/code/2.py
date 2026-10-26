import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt


class FilmDialog(QDialog):
    def __init__(self, dialog_ui_path: Path, db_path: Path, film_id: int = None):
        super().__init__()

        # Загрузка формы диалога
        uic.loadUi(str(dialog_ui_path), self)

        self.db_path = db_path
        self.film_id = film_id
        self.genres_map = {}

        # Инициализация списка жанров и предзаполнение полей при редактировании
        self.load_genres()
        if self.film_id is not None:
            self.load_film_data()

        # Подключение обработчиков кнопок диалога
        self.btn_save.clicked.connect(self.validate_and_save)
        self.btn_cancel.clicked.connect(self.reject)

    def load_genres(self):
        # Загрузка жанров из базы данных в выпадающий список
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT id, title FROM genres ORDER BY title")
        for genre_id, title in cur.fetchall():
            self.genres_map[title] = genre_id
            self.combo_genre.addItem(title)
        con.close()

    def load_film_data(self):
        # Заполнение полей данными существующей записи
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute(
            "SELECT title, year, genre, duration FROM films WHERE id = ?",
            (self.film_id,)
        )
        film = cur.fetchone()
        con.close()

        if film:
            title, year, genre_id, duration = film
            self.edit_title.setText(str(title))
            self.edit_year.setText(str(year))
            self.edit_duration.setText(str(duration))

            # Установка текущего жанра по его идентификатору
            for g_name, g_id in self.genres_map.items():
                if g_id == genre_id:
                    self.combo_genre.setCurrentText(g_name)
                    break

    def validate_and_save(self):
        # Получение значений из формы
        title = self.edit_title.text().strip()
        year_str = self.edit_year.text().strip()
        duration_str = self.edit_duration.text().strip()
        genre_name = self.combo_genre.currentText()

        # Проверка обязательного заполнения названия
        if not title:
            QMessageBox.warning(self, "Ошибка ввода", "Название фильма не может быть пустым.")
            return

        # Проверка корректности введенного года
        try:
            year = int(year_str)
            current_year = datetime.now().year
            if year < 1895:
                QMessageBox.warning(self, "Ошибка ввода", "Год выпуска не может быть меньше 1895.")
                return
            if year > current_year + 5:
                QMessageBox.warning(self, "Ошибка ввода", f"Год выпуска не может быть больше {current_year + 5}.")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка ввода", "Год выпуска должен быть целым числом.")
            return

        # Проверка и ограничение продолжительности фильма по времени
        try:
            duration = int(duration_str)
            if duration <= 0:
                QMessageBox.warning(self, "Ошибка ввода", "Продолжительность фильма должна быть больше 0 минут.")
                return
            # Ограничение верхнего предела продолжительности (не более 600 минут / 10 часов)
            if duration > 600:
                QMessageBox.warning(self, "Ошибка ввода", "Продолжительность фильма не может превышать 600 минут (10 часов).")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка ввода", "Продолжительность должна быть целым числом.")
            return

        # Получение идентификатора жанра
        genre_id = self.genres_map.get(genre_name)
        if genre_id is None:
            QMessageBox.warning(self, "Ошибка ввода", "Не выбран жанр фильма.")
            return

        # Сохранение данных в базу данных
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        if self.film_id is None:
            # Создание новой записи
            cur.execute(
                "INSERT INTO films (title, year, genre, duration) VALUES (?, ?, ?, ?)",
                (title, year, genre_id, duration)
            )
        else:
            # Обновление существующей записи
            cur.execute(
                "UPDATE films SET title = ?, year = ?, genre = ?, duration = ? WHERE id = ?",
                (title, year, genre_id, duration, self.film_id)
            )

        con.commit()
        con.close()
        self.accept()


class FilmManager(QMainWindow):
    def __init__(self):
        super().__init__()

        # Определение путей к интерфейсам и базе данных
        current_dir = Path(__file__).resolve().parent
        main_ui_path = current_dir.parent / 'ui' / '2.ui'
        self.dialog_ui_path = current_dir.parent / 'ui' / 'dialog.ui'
        self.db_path = current_dir.parent / 'db' / 'films_db.sqlite'

        # Загрузка интерфейса главного окна
        uic.loadUi(str(main_ui_path), self)

        # Привязка обработчиков кнопок
        self.btn_add.clicked.connect(self.add_film)
        self.btn_edit.clicked.connect(self.edit_film)
        self.btn_delete.clicked.connect(self.delete_film)

        # Начальная загрузка записей
        self.load_data()

    def load_data(self):
        # Проверка доступности файла базы данных
        if not self.db_path.exists():
            QMessageBox.critical(self, "Ошибка", f"Файл базы данных не найден:\n{self.db_path}")
            return

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        # Извлечение данных фильма с текстовым представлением жанра
        cur.execute("""
            SELECT films.id, films.title, films.year, genres.title AS genre, films.duration
            FROM films
            LEFT JOIN genres ON films.genre = genres.id
            ORDER BY films.id
        """)
        rows = cur.fetchall()

        # Формирование заголовков колонок непосредственно из параметров курсора
        headers = [col[0] for col in cur.description]
        con.close()

        # Настройка таблицы
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setRowCount(len(rows))

        # Заполнение ячеек данными
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem()
                if isinstance(value, (int, float)):
                    item.setData(Qt.ItemDataRole.DisplayRole, value)
                else:
                    item.setText(str(value) if value is not None else "")
                self.tableWidget.setItem(row_idx, col_idx, item)

    def get_selected_film_id(self):
        # Получение идентификатора фильма из выбранной строки таблицы
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row_idx = selected_rows[0].row()
        return int(self.tableWidget.item(row_idx, 0).text())

    def add_film(self):
        # Открытие формы добавления новой записи
        dialog = FilmDialog(self.dialog_ui_path, self.db_path)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def edit_film(self):
        # Проверка наличия выделенной строки перед редактированием
        film_id = self.get_selected_film_id()
        if film_id is None:
            QMessageBox.warning(self, "Предупреждение", "Необходимо выделить запись для редактирования.")
            return

        # Открытие формы редактирования выделенной записи
        dialog = FilmDialog(self.dialog_ui_path, self.db_path, film_id=film_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def delete_film(self):
        # Проверка наличия выделенной строки перед удалением
        film_id = self.get_selected_film_id()
        if film_id is None:
            QMessageBox.warning(self, "Предупреждение", "Необходимо выделить запись для удаления.")
            return

        # Запрос подтверждения удаления
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить выбранную запись с ID {film_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("DELETE FROM films WHERE id = ?", (film_id,))
            con.commit()
            con.close()
            # Обновление отображения таблицы после удаления
            self.load_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FilmManager()
    window.show()
    sys.exit(app.exec())