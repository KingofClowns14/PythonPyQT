import sys
import hashlib
import sqlite3
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Определение базовой папки проекта (папка 4)
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db' / 'library.db'


def hash_password(password: str) -> str:
    # Простое хеширование пароля через SHA-256
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_database():
    # Создание таблиц пользователей и книг, если они не существуют
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL,
                genre TEXT NOT NULL,
                image_path TEXT
            )
        """)
        conn.commit()


class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        ui_path = BASE_DIR / 'ui' / 'auth.ui'
        uic.loadUi(str(ui_path), self)

        self.btnLogin.clicked.connect(self.handle_login)
        self.btnRegister.clicked.connect(self.handle_register)

    def handle_login(self):
        username = self.editUsername.text().strip()
        password = self.editPassword.text()

        if not username or not password:
            self.labelStatus.setText("Заполните все поля")
            return

        pwd_hash = hash_password(password)
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND password_hash = ?",
                (username, pwd_hash)
            )
            if cursor.fetchone():
                self.accept()
            else:
                self.labelStatus.setText("Неверный логин или пароль")

    def handle_register(self):
        username = self.editUsername.text().strip()
        password = self.editPassword.text()

        if not username or not password:
            self.labelStatus.setText("Заполните все поля")
            return

        pwd_hash = hash_password(password)
        try:
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, pwd_hash)
                )
                conn.commit()
            QMessageBox.information(self, "Успех", "Пользователь зарегистрирован")
            self.labelStatus.setText("")
        except sqlite3.IntegrityError:
            self.labelStatus.setText("Логин уже занят")


class BookDialog(QDialog):
    def __init__(self, book_data: dict = None):
        super().__init__()
        self.book_data = book_data or {}
        ui_path = BASE_DIR / 'ui' / 'book_dialog.ui'
        uic.loadUi(str(ui_path), self)

        self.btnBrowseImage.clicked.connect(self.choose_image)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if self.book_data:
            self.setWindowTitle("Редактирование книги")
            self.editTitle.setText(self.book_data.get('title', ''))
            self.editAuthor.setText(self.book_data.get('author', ''))
            self.spinYear.setValue(int(self.book_data.get('year', 2024)))
            self.editGenre.setText(self.book_data.get('genre', ''))
            self.editImagePath.setText(self.book_data.get('image_path', '') or '')
        else:
            self.setWindowTitle("Добавление книги")

    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать обложку книги", str(BASE_DIR / 'img'), "Изображения (*.png *.jpg *.jpeg)"
        )
        if file_path:
            # Преобразование абсолютного пути в относительный путь от папки 4
            try:
                rel_path = Path(file_path).relative_to(BASE_DIR).as_posix()
            except ValueError:
                rel_path = file_path
            self.editImagePath.setText(rel_path)

    def get_data(self) -> dict:
        return {
            'title': self.editTitle.text().strip(),
            'author': self.editAuthor.text().strip(),
            'year': self.spinYear.value(),
            'genre': self.editGenre.text().strip(),
            'image_path': self.editImagePath.text().strip()
        }

    def accept(self):
        data = self.get_data()
        if not data['title'] or not data['author'] or not data['genre']:
            QMessageBox.warning(self, "Ошибка", "Заполните название, автора и жанр")
            return
        super().accept()


class LibraryMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = BASE_DIR / 'ui' / '6.ui'
        uic.loadUi(str(ui_path), self)

        self.default_cover = BASE_DIR / 'img' / 'default_book.png'
        self.books = []

        self.setup_ui()
        self.load_books()

    def setup_ui(self):
        self.tableBooks.setColumnCount(5)
        self.tableBooks.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Год", "Жанр"])
        self.tableBooks.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableBooks.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tableBooks.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.tableBooks.itemSelectionChanged.connect(self.display_selected_book)
        self.editSearchTitle.textChanged.connect(self.load_books)
        self.editSearchAuthor.textChanged.connect(self.load_books)
        self.btnResetSearch.clicked.connect(self.reset_search)

        self.btnAdd.clicked.connect(self.add_book)
        self.btnEdit.clicked.connect(self.edit_book)
        self.btnDelete.clicked.connect(self.delete_book)

    def reset_search(self):
        self.editSearchTitle.clear()
        self.editSearchAuthor.clear()

    def load_books(self):
        title_q = self.editSearchTitle.text().strip()
        author_q = self.editSearchAuthor.text().strip()

        query = "SELECT id, title, author, year, genre, image_path FROM books WHERE 1=1"
        params = []
        if title_q:
            query += " AND title LIKE ?"
            params.append(f"%{title_q}%")
        if author_q:
            query += " AND author LIKE ?"
            params.append(f"%{author_q}%")
        query += " ORDER BY id DESC"

        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        self.books = [
            {'id': r[0], 'title': r[1], 'author': r[2], 'year': r[3], 'genre': r[4], 'image_path': r[5]}
            for r in rows
        ]

        self.tableBooks.setRowCount(len(self.books))
        for row_idx, book in enumerate(self.books):
            self.tableBooks.setItem(row_idx, 0, QTableWidgetItem(str(book['id'])))
            self.tableBooks.setItem(row_idx, 1, QTableWidgetItem(book['title']))
            self.tableBooks.setItem(row_idx, 2, QTableWidgetItem(book['author']))
            self.tableBooks.setItem(row_idx, 3, QTableWidgetItem(str(book['year'])))
            self.tableBooks.setItem(row_idx, 4, QTableWidgetItem(book['genre']))

        if self.books:
            self.tableBooks.selectRow(0)
        else:
            self.clear_card()

    def get_selected_book(self):
        selected = self.tableBooks.selectionModel().selectedRows()
        if not selected:
            return None
        return self.books[selected[0].row()]

    def display_selected_book(self):
        book = self.get_selected_book()
        if not book:
            self.clear_card()
            return

        self.infoTitle.setText(f"Название: {book['title']}")
        self.infoAuthor.setText(f"Автор: {book['author']}")
        self.infoYear.setText(f"Год издания: {book['year']}")
        self.infoGenre.setText(f"Жанр: {book['genre']}")

        img_path = self.default_cover
        if book['image_path']:
            custom_path = BASE_DIR / book['image_path']
            if custom_path.exists():
                img_path = custom_path

        if img_path.exists():
            pix = QPixmap(str(img_path))
            self.lblCover.setPixmap(
                pix.scaled(240, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self.lblCover.clear()
            self.lblCover.setText("Нет обложки")

    def clear_card(self):
        self.infoTitle.setText("Название: -")
        self.infoAuthor.setText("Автор: -")
        self.infoYear.setText("Год издания: -")
        self.infoGenre.setText("Жанр: -")
        self.lblCover.clear()

    def add_book(self):
        dialog = BookDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO books (title, author, year, genre, image_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['title'], data['author'], data['year'], data['genre'], data['image_path']))
                conn.commit()
            self.load_books()

    def edit_book(self):
        book = self.get_selected_book()
        if not book:
            QMessageBox.warning(self, "Предупреждение", "Выберите книгу для редактирования")
            return

        dialog = BookDialog(book)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE books
                    SET title = ?, author = ?, year = ?, genre = ?, image_path = ?
                    WHERE id = ?
                """, (data['title'], data['author'], data['year'], data['genre'], data['image_path'], book['id']))
                conn.commit()
            self.load_books()

    def delete_book(self):
        book = self.get_selected_book()
        if not book:
            QMessageBox.warning(self, "Предупреждение", "Выберите книгу для удаления")
            return

        confirm = QMessageBox.question(
            self, "Удаление", f"Удалить книгу «{book['title']}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE id = ?", (book['id'],))
                conn.commit()
            self.load_books()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    init_database()

    auth = AuthDialog()
    if auth.exec() == QDialog.DialogCode.Accepted:
        main_win = LibraryMainWindow()
        main_win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)