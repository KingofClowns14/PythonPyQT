# Главная точка входа в приложение «Кулинарная книга и калькулятор калорий».
# Содержит конфигурацию приложения, обработку глобальных исключений и запуск цикла событий Qt.

import sys
from PyQt6.QtWidgets import QApplication

# Выбор версии для запуска:
# Для работы с XML используем ui_windows:
from ui_windows import MainWindow

# ГЛОБАЛЬНЫЕ КОНСТАНТЫ
APPLICATION_NAME = "Кулинарная книга и калькулятор калорий"
ORGANIZATION_NAME = "MyUniversityApp"
APP_VERSION = "1.0.0"

def setup_application() -> QApplication:
    # Создание и предварительная настройка экземпляра QApplication.
    app = QApplication(sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setApplicationVersion(APP_VERSION)
    return app


def main() -> None:
    # Основная функция инициализации и запуска оконного интерфейса.
    app = setup_application()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()