# launcher.py
import pygame
from ui_menu import Menu
from catcher_game import run_catcher

pygame.display.set_caption("nowpy")

def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 562), pygame.SCALED | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()

    menu = Menu(screen)
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            menu.handle_event(ev)

        menu.update()
        menu.draw()
        pygame.display.flip()
        clock.tick(60)

        if menu.play_clicked:
            # 当 Play 被点击，要求输入 .osz 路径
            menu.play_clicked = False
            from file_dialog import choose_osz_file
            osz_path = choose_osz_file()
            if not osz_path:
                print("未选择文件，返回主菜单。")
                continue

            try:
                run_catcher(osz_path, screen)
            except Exception as e:
                print("游戏运行出错：", e)

    pygame.quit()

if __name__ == "__main__":
    main()
