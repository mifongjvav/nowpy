# ui_menu.py
import pygame
from animation import Tween


class Menu:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.cx = screen.get_width() // 2
        self.cy = screen.get_height() // 2

        # 背景
        self.bg = pygame.Surface(screen.get_size())
        self.bg.fill((40, 40, 40))

        # === Logo ===
        try:
            raw_logo = pygame.image.load("logo.png").convert_alpha()
            self.logo = pygame.transform.smoothscale(raw_logo, (256, 256))
        except Exception as e:
            print("Logo 加载失败：", e)
            self.logo = pygame.Surface((256, 256))
            self.logo.fill((100, 100, 255))

        self.logo_rect = self.logo.get_rect()

        self.logo_tween = Tween(
            start=-300,
            end=self.cy - 120,
            duration=0.8,
        )

        # === Play 按钮 ===
        try:
            self.play_img = pygame.image.load("UI/play.png").convert_alpha()
        except Exception as e:
            print("Play 按钮加载失败：", e)
            self.play_img = pygame.Surface((200, 80))
            self.play_img.fill((50, 200, 50))

        self.play_rect = self.play_img.get_rect()

        self.play_tween = Tween(
            start=self.screen.get_height() + 100,
            end=self.cy + 40,
            duration=0.9,
        )

        self.hover = False
        self.play_clicked = False

    def handle_event(self, ev: pygame.event.Event):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.play_rect.collidepoint(ev.pos)

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.play_rect.collidepoint(ev.pos):
                self.play_clicked = True

    def update(self):
        self.logo_y = self.logo_tween.update()
        self.play_y = self.play_tween.update()

    def draw(self):
        self.screen.blit(self.bg, (0, 0))

        # Logo（动画）
        self.logo_rect.center = (self.cx, int(self.logo_y))
        self.screen.blit(self.logo, self.logo_rect)

        # Play（动画）
        self.play_rect.center = (self.cx, int(self.play_y))

        img = self.play_img
        if self.hover:
            img = self.play_img.copy()
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 40))
            img.blit(overlay, (0, 0))

        self.screen.blit(img, self.play_rect)
