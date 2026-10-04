
# Модуль работы с реляционной базой данных SQLite.
# Реализует полный цикл CRUD для двух связанных таблиц:
# - recipes (рецепты)
# - ingredients (ингредиенты блюда)

import sqlite3
from typing import List, Tuple, Optional

# Имя файла базы данных по умолчанию
DEFAULT_DB_NAME = "recipes.db"

class Database:
    # Класс-менеджер для взаимодействия с SQLite базой данных.

    def __init__(self, db_name: str = DEFAULT_DB_NAME) -> None:
        # Инициализация соединения и автоматическое создание таблиц.
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        # Включение поддержки внешних ключей в SQLite
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()

    def create_tables(self) -> None:
        # Создает таблицы рецептов и ингредиентов при их отсутствии.
        # Таблица 1: Рецепты блюд
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                image_path TEXT,
                total_calories INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Таблица 2: Ингредиенты, привязанные к конкретному рецепту
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                calories_per_100g REAL NOT NULL,
                weight_g REAL NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """)
        self.connection.commit()

    # ОПЕРАЦИИ С РЕЦЕПТАМИ

    def add_recipe(self, title: str, description: str, 
                   image_path: str, total_calories: int) -> int:
        # Создание новой записи рецепта.Возвращает ID созданной записи.
        query = """
            INSERT INTO recipes (title, description, image_path, total_calories)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(query, (title, description, image_path, total_calories))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_all_recipes(self) -> List[Tuple]:
        # Чтение всех рецептов из базы данных.
        query = "SELECT id, title, description, image_path, total_calories FROM recipes ORDER BY id DESC"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Tuple]:
        # Получение конкретного рецепта по первичному ключу (SELECT).
        query = "SELECT id, title, description, image_path, total_calories FROM recipes WHERE id = ?"
        self.cursor.execute(query, (recipe_id,))
        return self.cursor.fetchone()

    def update_recipe(self, recipe_id: int, title: str, description: str, 
                      image_path: str, total_calories: int) -> None:
        # Изменение существующего рецепта (UPDATE).
        # Закрывает требование критерия 3.e по изменению данных в БД.
        query = """
            UPDATE recipes
            SET title = ?, description = ?, image_path = ?, total_calories = ?
            WHERE id = ?
        """
        self.cursor.execute(query, (title, description, image_path, total_calories, recipe_id))
        self.connection.commit()

    def delete_recipe(self, recipe_id: int) -> None:
        # Удаление рецепта и всех связанных ингредиентов (DELETE).
        self.cursor.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
        self.cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        self.connection.commit()

    # ОПЕРАЦИИ С ИНГРЕДИЕНТАМИ

    def add_ingredient(self, recipe_id: int, name: str, 
                       calories_per_100g: float, weight_g: float) -> int:
        # Добавление ингредиента к рецепту (INSERT в таблицу 2).
        query = """
            INSERT INTO ingredients (recipe_id, name, calories_per_100g, weight_g)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(query, (recipe_id, name, calories_per_100g, weight_g))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_recipe_ingredients(self, recipe_id: int) -> List[Tuple]:
        # Получение списка всех ингредиентов для блюда.
        query = """
            SELECT id, name, calories_per_100g, weight_g
            FROM ingredients
            WHERE recipe_id = ?
            ORDER BY id ASC
        """
        self.cursor.execute(query, (recipe_id,))
        return self.cursor.fetchall()

    def clear_recipe_ingredients(self, recipe_id: int) -> None:
        # Удаление всех старых ингредиентов рецепта при его обновлении.
        self.cursor.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
        self.connection.commit()

    def calculate_total_calories(self, recipe_id: int) -> int:
        # Расчет суммарной калорийности на основе записей в таблице ингредиентов.
        # Формула: (вес / 100) * калорийность_на_100г
        ingredients = self.get_recipe_ingredients(recipe_id)
        total = 0.0
        for _, _, cal_100, weight in ingredients:
            total += (weight / 100.0) * cal_100
        return int(round(total))

    def close(self) -> None:
        # Безопасное закрытие соединения с базой данных.
        self.connection.close()