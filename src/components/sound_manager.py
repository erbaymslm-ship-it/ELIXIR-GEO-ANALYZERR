"""
ELIXIR TECHNOLOGY
Ses Yonetimi - Buzzer/Bip Sesleri
"""

import struct
import math
import os
import io
from kivy.core.audio import SoundLoader
from kivy.logger import Logger
from kivy.utils import platform


class SoundManager:
    _instance = None

    @staticmethod
    def get_instance():
        if SoundManager._instance is None:
            SoundManager._instance = SoundManager()
        return SoundManager._instance

    def __init__(self):
        self.sounds = {}
        self._generate_sounds()

    def _generate_wav(self, frequency, duration_ms, volume=0.5):
        sample_rate = 22050
        num_samples = int(sample_rate * duration_ms / 1000)
        samples = []
        for i in range(num_samples):
            t = i / sample_rate
            fade = 1.0
            fade_samples = int(sample_rate * 0.01)
            if i < fade_samples:
                fade = i / fade_samples
            elif i > num_samples - fade_samples:
                fade = (num_samples - i) / fade_samples
            val = volume * fade * math.sin(2 * math.pi * frequency * t)
            samples.append(int(val * 32767))

        wav_data = io.BytesIO()
        data_size = num_samples * 2
        wav_data.write(b'RIFF')
        wav_data.write(struct.pack('<I', 36 + data_size))
        wav_data.write(b'WAVE')
        wav_data.write(b'fmt ')
        wav_data.write(struct.pack('<IHHIIHH', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        wav_data.write(b'data')
        wav_data.write(struct.pack('<I', data_size))
        for s in samples:
            wav_data.write(struct.pack('<h', s))

        return wav_data.getvalue()

    def _generate_sounds(self):
        try:
            if platform == 'android':
                sound_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds')
            else:
                sound_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds')

            os.makedirs(sound_dir, exist_ok=True)

            sound_defs = {
                'beep_low': (400, 80, 0.3),
                'beep_medium': (700, 60, 0.4),
                'beep_high': (1200, 40, 0.5),
                'beep_very_high': (1800, 30, 0.6),
                'data_receive': (880, 50, 0.25),
                'scan_complete': (1000, 200, 0.4),
                'error': (300, 300, 0.3),
                'connect': (600, 150, 0.3),
            }

            for name, (freq, dur, vol) in sound_defs.items():
                filepath = os.path.join(sound_dir, f'{name}.wav')
                if not os.path.exists(filepath):
                    wav_data = self._generate_wav(freq, dur, vol)
                    with open(filepath, 'wb') as f:
                        f.write(wav_data)

                sound = SoundLoader.load(filepath)
                if sound:
                    self.sounds[name] = sound
        except Exception as e:
            Logger.error(f"SoundManager: Ses olusturma hatasi: {e}")

    def play(self, sound_name):
        try:
            if sound_name in self.sounds and self.sounds[sound_name]:
                self.sounds[sound_name].play()
        except Exception as e:
            Logger.warning(f"SoundManager: Ses calma hatasi: {e}")

    def play_beep_for_value(self, value):
        if value < 200:
            self.play('beep_low')
        elif value < 500:
            self.play('beep_medium')
        elif value < 800:
            self.play('beep_high')
        else:
            self.play('beep_very_high')
