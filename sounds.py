# sounds.py
import pygame
import os
import random

class SoundsManager:
    def __init__(self, sounds_dir="sounds"):
        self.sounds_dir = sounds_dir
        self.hit_sounds = []
        self.miss_sound = None
        if os.path.isdir(sounds_dir):
            for f in os.listdir(sounds_dir):
                fp = os.path.join(sounds_dir, f)
                if not os.path.isfile(fp):
                    continue
                if f.lower() == "miss.wav":
                    try:
                        self.miss_sound = pygame.mixer.Sound(fp)
                    except Exception:
                        self.miss_sound = None
                    continue
                if f.lower().endswith((".wav", ".mp3", ".ogg")):
                    try:
                        s = pygame.mixer.Sound(fp)
                        self.hit_sounds.append(s)
                    except Exception:
                        pass
        # 若没有任何打击音效，生成一个简单 beep
        if not self.hit_sounds:
            # 生成短静音占位（pygame 不能轻易合成，这里留空）
            pass

    def play_hit(self, left=1.0, right=1.0):
        if not self.hit_sounds:
            return
        s = random.choice(self.hit_sounds)
        ch = s.play()
        if ch:
            try:
                ch.set_volume(left, right)
            except Exception:
                # 某些 pygame 版本只支持单一音量参数
                ch.set_volume((left+right)/2)

    def play_miss(self, left=1.0, right=1.0):
        if self.miss_sound:
            ch = self.miss_sound.play()
            if ch:
                try:
                    ch.set_volume(left, right)
                except Exception:
                    ch.set_volume((left+right)/2)
