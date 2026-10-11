import sys
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import QApplication, QMainWindow


class PianoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса
        current_dir = Path(__file__).resolve().parent
        ui_file_path = current_dir.parent / 'ui' / '7.ui'
        uic.loadUi(str(ui_file_path), self)

        # Каталог со звуковыми файлами
        self.sounds_dir = current_dir.parent / 'sounds'

        # Словарь звуковых эффектов
        self.sound_effects = {}
        self.init_sounds()

        # Привязка клавиш фортепиано
        self.btn_c.clicked.connect(lambda: self.play_sound('C4'))
        self.btn_d.clicked.connect(lambda: self.play_sound('D4'))
        self.btn_e.clicked.connect(lambda: self.play_sound('E4'))
        self.btn_f.clicked.connect(lambda: self.play_sound('F4'))
        self.btn_g.clicked.connect(lambda: self.play_sound('G4'))
        self.btn_a.clicked.connect(lambda: self.play_sound('A4'))
        self.btn_b.clicked.connect(lambda: self.play_sound('B4'))
        self.btn_c2.clicked.connect(lambda: self.play_sound('C5'))

        # Привязка кнопок альта (viola)
        self.btn_v_a3.clicked.connect(lambda: self.play_sound('viola_A3'))
        self.btn_v_a4.clicked.connect(lambda: self.play_sound('viola_A4'))
        self.btn_v_a4_1.clicked.connect(lambda: self.play_sound('viola_A4_1'))
        self.btn_v_a4_2.clicked.connect(lambda: self.play_sound('viola_A4_2'))
        self.btn_v_a5.clicked.connect(lambda: self.play_sound('viola_A5'))

    def init_sounds(self):
        # Инициализация всех загруженных аудиофайлов
        audio_keys = [
            'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5',
            'viola_A3', 'viola_A4', 'viola_A4_1', 'viola_A4_2', 'viola_A5'
        ]

        for key in audio_keys:
            file_path = self.sounds_dir / f"{key}.wav"
            if file_path.exists():
                effect = QSoundEffect(self)
                effect.setSource(QUrl.fromLocalFile(str(file_path.resolve())))
                effect.setVolume(0.2)
                self.sound_effects[key] = effect

    def play_sound(self, sound_name):
        # Воспроизведение выбранного аудиоэффекта
        effect = self.sound_effects.get(sound_name)
        if effect:
            if effect.isPlaying():
                effect.stop()
            effect.play()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PianoApp()
    window.show()
    sys.exit(app.exec())