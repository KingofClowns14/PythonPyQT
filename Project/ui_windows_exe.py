# Модуль интерфейса для сборки Standalone .EXE версии.
# Использует скомпилированные классы ui_main, ui_add, ui_view.

import os
import re
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QDialog, QMessageBox, QFileDialog, QMenu,
    QListWidgetItem, QTableWidgetItem, QHeaderView,
    QInputDialog, QStyledItemDelegate, QDoubleSpinBox, QLineEdit
)
from PyQt6.QtCore import Qt, QUrl, QRegularExpression
from PyQt6.QtGui import QPixmap, QAction, QRegularExpressionValidator
from PyQt6.QtMultimedia import QSoundEffect

from database import Database

# Импорт сгенерированных классов интерфейса
from ui.ui_main import Ui_MainWindow
from ui.ui_add import Ui_AddDialog
from ui.ui_view import Ui_ViewDialog


# Константы
MUSIC_VOLUME = 0.3
SFX_VOLUME_DELETE = 1.0
SFX_VOLUME_ADD = 0.2
DEFAULT_IMAGE_NAME = "default_food.png"


def get_resource_path(relative_path: str) -> Path:
    # Универсальное получение абсолютного пути к ресурсам для PyInstaller.
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent
    return base_dir / relative_path


class NumericDelegate(QStyledItemDelegate):
    def __init__(self, min_val: float, max_val: float, decimals: int = 1, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.decimals = decimals

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(self.min_val)
        editor.setMaximum(self.max_val)
        editor.setDecimals(self.decimals)
        editor.setSingleStep(10.0 if self.max_val > 1000 else 1.0)
        return editor

    def setEditorData(self, editor, index):
        raw_val = index.model().data(index, Qt.ItemDataRole.EditRole) or "0"
        try:
            val = float(str(raw_val).replace(',', '.').strip())
        except ValueError:
            val = self.min_val
        editor.setValue(val)

    def setModelData(self, editor, model, index):
        model.setData(index, f"{editor.value():.{self.decimals}f}", Qt.ItemDataRole.EditRole)


class IngredientNameDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setFrame(False)
        regex = QRegularExpression(r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-]*$")
        validator = QRegularExpressionValidator(regex, editor)
        editor.setValidator(validator)
        editor.setMaxLength(50)
        return editor


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.db = Database(str(get_resource_path("recipes.db")))
        # Звуки
        self.wait_music = QSoundEffect()
        self.wait_music.setSource(QUrl.fromLocalFile(str(get_resource_path("assets/wait.wav"))))
        self.wait_music.setLoopCount(-2)
        self.wait_music.setVolume(MUSIC_VOLUME)
        self.wait_music.play()
        self.delete_sound = QSoundEffect()
        self.delete_sound.setSource(QUrl.fromLocalFile(str(get_resource_path("assets/delete.wav"))))
        self.delete_sound.setVolume(SFX_VOLUME_DELETE)
        self.add_sound = QSoundEffect()
        self.add_sound.setSource(QUrl.fromLocalFile(str(get_resource_path("assets/add.wav"))))
        self.add_sound.setVolume(SFX_VOLUME_ADD)
        self.load_recipes()
        self.btnAdd.clicked.connect(self.open_add_dialog)
        self.btnSearch.clicked.connect(self.trigger_search)
        self.btnResetSearch.clicked.connect(self.reset_search)
        self.listWidget.itemDoubleClicked.connect(self.open_view_dialog)

    def trigger_search(self) -> None:
        text, ok = QInputDialog.getText(self, "Поиск блюда", "Введите название рецепта:")
        if ok:
            search_text = text.strip()
            if search_text:
                self.load_recipes(search_query=search_text)
            else:
                self.reset_search()

    def reset_search(self) -> None:
        self.load_recipes(search_query="")

    def load_recipes(self, search_query: str = "") -> None:
        all_recipes = self.db.get_all_recipes()
        query = search_query.strip().lower()

        if query:
            filtered_recipes = [r for r in all_recipes if query in r[1].lower()]
            if not filtered_recipes:
                QMessageBox.information(
                    self,
                    "Результаты поиска",
                    f"По запросу «{search_query}» ничего не найдено!\nСписок рецептов возвращен к исходному виду."
                )
                matching_recipes = all_recipes
                self.btnResetSearch.setVisible(False)
            else:
                matching_recipes = filtered_recipes
                self.btnResetSearch.setText(f"Показать все рецепты (найдено: {len(matching_recipes)})")
                self.btnResetSearch.setVisible(True)
        else:
            matching_recipes = all_recipes
            self.btnResetSearch.setVisible(False)

        self.listWidget.clear()
        for recipe in matching_recipes:
            recipe_id, title, _, _, total_cal = recipe
            item = QListWidgetItem(f"{title} — {total_cal} ккал")
            item.setData(Qt.ItemDataRole.UserRole, recipe_id)
            self.listWidget.addItem(item)

    def open_view_dialog(self, item: QListWidgetItem) -> None:
        recipe_id = item.data(Qt.ItemDataRole.UserRole)
        recipe_data = self.db.get_recipe_by_id(recipe_id)
        if recipe_data:
            dialog = ViewRecipeDialog(recipe_data, self.db, self)
            dialog.exec()
            self.load_recipes()

    def open_add_dialog(self) -> None:
        dialog = AddEditRecipeDialog(self.db, recipe_id=None, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.add_sound.play()
            self.load_recipes()

    def open_edit_dialog(self, recipe_id: int) -> None:
        dialog = AddEditRecipeDialog(self.db, recipe_id=recipe_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.add_sound.play()
            self.load_recipes()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_recipe()
        elif event.key() == Qt.Key.Key_F and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.trigger_search()
        elif event.key() == Qt.Key.Key_Escape:
            self.reset_search()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            selected_items = self.listWidget.selectedItems()
            if selected_items:
                menu = QMenu(self)
                edit_action = QAction("Редактировать блюдо", self)
                delete_action = QAction("Удалить блюдо", self)
                menu.addAction(edit_action)
                menu.addAction(delete_action)
                action = menu.exec(event.globalPosition().toPoint())
                recipe_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
                if action == edit_action:
                    self.open_edit_dialog(recipe_id)
                elif action == delete_action:
                    self.delete_selected_recipe()
        super().mousePressEvent(event)

    def delete_selected_recipe(self) -> None:
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        recipe_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы действительно хотите удалить этот рецепт?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_recipe(recipe_id)
            self.delete_sound.play()
            self.load_recipes()


class ViewRecipeDialog(QDialog, Ui_ViewDialog):
    def __init__(self, recipe_data: tuple, db: Database, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.db = db
        self.recipe_id = recipe_data[0]
        self.recipe_data = recipe_data
        self.tableIngredients.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.labelTitle.setText(recipe_data[1])
        self.labelCalories.setText(f"Общая калорийность: {recipe_data[4]} ккал")
        self.btnEdit.clicked.connect(self.trigger_edit)
        self.btnClose.clicked.connect(self.close)
        self.original_pixmap = None
        image_path = recipe_data[3]
        if os.path.exists(image_path):
            self.original_pixmap = QPixmap(image_path)
            self.update_image()
        else:
            self.imageLabel.setText("Фотография отсутствует")

        self.load_ingredients()

    def load_ingredients(self) -> None:
        ingredients = self.db.get_recipe_ingredients(self.recipe_id)
        self.tableIngredients.setRowCount(len(ingredients))
        for row, ing in enumerate(ingredients):
            _, name, cal_100, weight = ing
            self.tableIngredients.setItem(row, 0, QTableWidgetItem(str(name)))
            self.tableIngredients.setItem(row, 1, QTableWidgetItem(f"{weight:.1f}"))
            self.tableIngredients.setItem(row, 2, QTableWidgetItem(f"{cal_100:.1f}"))

    def trigger_edit(self) -> None:
        dialog = AddEditRecipeDialog(self.db, recipe_id=self.recipe_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = self.db.get_recipe_by_id(self.recipe_id)
            if updated:
                self.recipe_data = updated
                self.labelTitle.setText(updated[1])
                self.labelCalories.setText(f"Общая калорийность: {updated[4]} ккал")
                if os.path.exists(updated[3]):
                    self.original_pixmap = QPixmap(updated[3])
                    self.update_image()
                self.load_ingredients()

    def update_image(self) -> None:
        if self.original_pixmap and not self.original_pixmap.isNull():
            target_w = max(self.imageLabel.width() - 10, 360)
            target_h = max(self.imageLabel.height() - 10, 220)
            scaled = self.original_pixmap.scaled(
                target_w, target_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.imageLabel.setPixmap(scaled)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_image()


class AddEditRecipeDialog(QDialog, Ui_AddDialog):
    def __init__(self, db: Database, recipe_id: Optional[int] = None, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.db = db
        self.recipe_id = recipe_id
        self.image_path = str(get_resource_path(f"assets/{DEFAULT_IMAGE_NAME}"))
        self.tableIngredients.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableIngredients.setItemDelegateForColumn(0, IngredientNameDelegate(self))
        self.tableIngredients.setItemDelegateForColumn(1, NumericDelegate(0.1, 20000.0, 1, self))
        self.tableIngredients.setItemDelegateForColumn(2, NumericDelegate(0.0, 1000.0, 1, self))
        self.tableIngredients.cellChanged.connect(self.recalculate_calories)
        self.btnAddIngredient.clicked.connect(self.add_ingredient_row)
        self.btnRemoveIngredient.clicked.connect(self.remove_ingredient_row)
        self.btnSelectImage.clicked.connect(self.select_image)
        self.btnSave.clicked.connect(self.save_recipe)
        if self.recipe_id is not None:
            self.setWindowTitle("Редактировать рецепт")
            self.btnSave.setText("Сохранить изменения")
            self.load_existing_recipe()

    def add_ingredient_row(self) -> None:
        row = self.tableIngredients.rowCount()
        self.tableIngredients.blockSignals(True)
        self.tableIngredients.insertRow(row)
        self.tableIngredients.setItem(row, 0, QTableWidgetItem("Ингредиент"))
        self.tableIngredients.setItem(row, 1, QTableWidgetItem("100.0"))
        self.tableIngredients.setItem(row, 2, QTableWidgetItem("50.0"))
        self.tableIngredients.blockSignals(False)
        self.recalculate_calories()

    def remove_ingredient_row(self) -> None:
        current_row = self.tableIngredients.currentRow()
        if current_row >= 0:
            self.tableIngredients.removeRow(current_row)
            self.recalculate_calories()

    def recalculate_calories(self) -> None:
        total_cal = 0.0
        for row in range(self.tableIngredients.rowCount()):
            weight_item = self.tableIngredients.item(row, 1)
            cal_item = self.tableIngredients.item(row, 2)
            try:
                w_str = weight_item.text().replace(',', '.').strip() if weight_item else "0"
                c_str = cal_item.text().replace(',', '.').strip() if cal_item else "0"
                weight = float(w_str)
                cal_100 = float(c_str)
                if weight > 0 and cal_100 >= 0:
                    total_cal += (weight / 100.0) * cal_100
            except ValueError:
                continue
        self.spinBoxCalories.setValue(int(round(total_cal)))

    def load_existing_recipe(self) -> None:
        recipe = self.db.get_recipe_by_id(self.recipe_id)
        if not recipe:
            return
        _, title, _, image_path, total_calories = recipe
        self.lineEditTitle.setText(title)
        self.spinBoxCalories.setValue(total_calories)
        self.image_path = image_path
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.imageLabel.setPixmap(pixmap.scaled(
                360, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        ingredients = self.db.get_recipe_ingredients(self.recipe_id)
        self.tableIngredients.blockSignals(True)
        self.tableIngredients.setRowCount(len(ingredients))
        for row, ing in enumerate(ingredients):
            _, name, cal_100, weight = ing
            self.tableIngredients.setItem(row, 0, QTableWidgetItem(str(name)))
            self.tableIngredients.setItem(row, 1, QTableWidgetItem(f"{weight:.1f}"))
            self.tableIngredients.setItem(row, 2, QTableWidgetItem(f"{cal_100:.1f}"))
        self.tableIngredients.blockSignals(False)
        self.recalculate_calories()

    def select_image(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выбрать фото блюда", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(self.image_path)
            target_w = max(self.imageLabel.width() - 10, 360)
            target_h = max(self.imageLabel.height() - 10, 220)
            scaled = pixmap.scaled(
                target_w, target_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.imageLabel.setPixmap(scaled)

    def validate_inputs(self) -> Optional[list]:
        errors = []
        title = self.lineEditTitle.text().strip()

        if not title:
            errors.append("• Название блюда не может быть пустым.")
        else:
            if len(title) < 2 or len(title) > 60:
                errors.append("• Название блюда должно содержать от 2 до 60 символов.")
            if not re.fullmatch(r'^[a-zA-Zа-яА-ЯёЁ0-9\s\-]+$', title):
                errors.append("• В названии блюда недопустимые символы. Разрешены только буквы, цифры, пробел и дефис.")
            elif not re.search(r'[a-zA-Zа-яА-ЯёЁ]', title):
                errors.append("• Название блюда должно содержать хотя бы одну букву.")

        if self.tableIngredients.rowCount() == 0:
            errors.append("• Добавьте хотя бы один ингредиент в калькулятор состава.")

        validated_ingredients = []
        for row in range(self.tableIngredients.rowCount()):
            row_num = row + 1
            name_item = self.tableIngredients.item(row, 0)
            weight_item = self.tableIngredients.item(row, 1)
            cal_item = self.tableIngredients.item(row, 2)
            name = name_item.text().strip() if name_item else ""
            if not name:
                errors.append(f"• Строка {row_num}: название ингредиента не может быть пустым.")
            elif not re.fullmatch(r'^[a-zA-Zа-яА-ЯёЁ0-9\s\-]+$', name):
                errors.append(f"• Строка {row_num} («{name}»): недопустимые символы! Только буквы, цифры, пробел и дефис.")
            elif not re.search(r'[a-zA-Zа-яА-ЯёЁ]', name):
                errors.append(f"• Строка {row_num} («{name}»): название должно содержать хотя бы одну букву.")

            try:
                w_str = weight_item.text().replace(',', '.').strip() if weight_item else ""
                weight = float(w_str)
                if weight <= 0:
                    errors.append(f"• Строка {row_num} ({name or 'без имени'}): вес должен быть больше 0.")
                elif weight > 20000:
                    errors.append(f"• Строка {row_num} ({name or 'без имени'}): вес не может превышать 20 000 г.")
            except ValueError:
                errors.append(f"• Строка {row_num} ({name or 'без имени'}): некорректный вес.")
                weight = 0.0

            try:
                c_str = cal_item.text().replace(',', '.').strip() if cal_item else ""
                cal_100 = float(c_str)
                if cal_100 < 0:
                    errors.append(f"• Строка {row_num} ({name or 'без имени'}): калорийность не может быть отрицательной.")
                elif cal_100 > 1000:
                    errors.append(f"• Строка {row_num} ({name or 'без имени'}): калорийность не может превышать 1000 ккал.")
            except ValueError:
                errors.append(f"• Строка {row_num} ({name or 'без имени'}): некорректная калорийность.")
                cal_100 = 0.0

            validated_ingredients.append((name, cal_100, weight))

        if errors:
            full_error_text = "Обнаружены следующие ошибки:\n\n" + "\n".join(errors)
            QMessageBox.warning(self, "Ошибки заполнения", full_error_text)
            return None

        return validated_ingredients

    def save_recipe(self) -> None:
        validated_ingredients = self.validate_inputs()
        if validated_ingredients is None:
            return

        title = self.lineEditTitle.text().strip()
        total_calories = self.spinBoxCalories.value()

        if self.recipe_id is None:
            saved_id = self.db.add_recipe(title, "Описание блюда", self.image_path, total_calories)
        else:
            saved_id = self.recipe_id
            self.db.update_recipe(saved_id, title, "Описание блюда", self.image_path, total_calories)
            self.db.clear_recipe_ingredients(saved_id)

        for name, cal_100, weight in validated_ingredients:
            self.db.add_ingredient(saved_id, name, cal_100, weight)

        self.accept()