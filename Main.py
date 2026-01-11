import pygame
import os

os.environ["SDL_RENDER_DRIVER"] = "opengl"

# 核心：一个简单的动画函数
def 平滑动画(当前值, 目标值, 速度=0.1):
    """
    最简单的平滑动画函数
    使用：当前值 = 平滑动画(当前值, 目标值, 速度)
    速度推荐：0.05-0.2，越小越慢越平滑
    """
    return 当前值 + (目标值 - 当前值) * 速度

def 触摸亮度变化(当前亮度, 鼠标在按钮上, 悬停亮度=0.8, 正常亮度=1.0):
    """
    触摸/悬停时改变亮度
    :param 当前亮度: 当前亮度值（1.0为正常）
    :param 鼠标在按钮上: 鼠标是否在按钮上
    :param 悬停亮度: 悬停时的亮度（默认0.8，变暗）
    :param 正常亮度: 正常时的亮度（默认1.0，正常）
    :return: 新的亮度值
    """
    目标亮度 = 悬停亮度 if 鼠标在按钮上 else 正常亮度
    return 平滑动画(当前亮度, 目标亮度, 0.15)

def 按下亮度变化(当前亮度, 按钮被按下, 按下亮度=0.6, 悬停亮度=0.8, 正常亮度=1.0):
    """
    按下时改变亮度
    :param 当前亮度: 当前亮度值
    :param 按钮被按下: 按钮是否被按下
    :param 按下亮度: 按下时的亮度（默认0.6，更暗）
    :param 悬停亮度: 悬停时的亮度（默认0.8，变暗）
    :param 正常亮度: 正常时的亮度（默认1.0，正常）
    :return: 新的亮度值
    """
    if 按钮被按下:
        目标亮度 = 按下亮度
    else:
        目标亮度 = 悬停亮度  # 这里假设按下后回到悬停状态，你可以根据需求调整
    return 平滑动画(当前亮度, 目标亮度, 0.2)

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((900, 562), pygame.SCALED | pygame.DOUBLEBUF, vsync=1)
pygame.display.set_caption("nowpy")
clock = pygame.time.Clock()
dt = 0

# 加载图片
icon = pygame.image.load("./logo-dark.png").convert_alpha()
pygame.display.set_icon(icon)

底 = pygame.image.load("./UI/底.png").convert_alpha()
logo原始 = pygame.image.load("./logo.png").convert_alpha()
play原始 = pygame.image.load("./UI/play.png").convert_alpha()

# 初始化状态
logo_x, logo_y = -100, 0
play_x, play_y = 50, 0
logo缩放 = 0.2
logo透明度 = 255

# 跟踪鼠标
鼠标在logo上 = False
鼠标在play上 = False
play被按下 = False

# Play按钮的亮度（1.0为正常，小于1.0变暗）
play亮度 = 1.0

# 主循环
运行中 = True
while 运行中:
    # 处理事件
    for 事件 in pygame.event.get():
        if 事件.type == pygame.QUIT:
            运行中 = False
        
        # 鼠标按下事件
        if 事件.type == pygame.MOUSEBUTTONDOWN and 事件.button == 1:  # 左键
            if 鼠标在play上:
                play被按下 = True
        
        # 鼠标释放事件
        if 事件.type == pygame.MOUSEBUTTONUP and 事件.button == 1:  # 左键
            if play被按下:
                play被按下 = False
                # 这里可以添加点击play后的操作，比如开始游戏
                print("Play按钮被点击！")
    
    # 获取鼠标位置
    鼠标位置 = pygame.mouse.get_pos()
    
    # 计算logo在屏幕上的位置（居中坐标系转换）
    logo屏幕x = screen.get_width() // 2 + logo_x
    logo屏幕y = screen.get_height() // 2 - logo_y
    logo当前大小 = (int(logo原始.get_width() * logo缩放), int(logo原始.get_height() * logo缩放))
    
    # 计算play在屏幕上的位置
    play屏幕x = screen.get_width() // 2 + play_x
    play屏幕y = screen.get_height() // 2 - play_y
    
    # 检查鼠标是否在logo上
    logo区域 = pygame.Rect(0, 0, logo当前大小[0], logo当前大小[1])
    logo区域.center = (logo屏幕x, logo屏幕y)
    鼠标在logo上 = logo区域.collidepoint(鼠标位置)
    
    # 检查鼠标是否在play上
    play区域 = pygame.Rect(0, 0, play原始.get_width(), play原始.get_height())
    play区域.center = (play屏幕x, play屏幕y)
    鼠标在play上 = play区域.collidepoint(鼠标位置)
    
    # 使用简单的动画函数更新状态
    if 鼠标在logo上:
        logo缩放 = 平滑动画(logo缩放, 0.22, 0.08)  # 鼠标悬停时放大
    else:
        logo缩放 = 平滑动画(logo缩放, 0.2, 0.08)   # 正常大小
    
    # 限制缩放范围
    logo缩放 = max(0.15, min(0.25, logo缩放))
    
    # 更新play按钮的亮度
    play亮度 = 触摸亮度变化(play亮度, 鼠标在play上)
    
    # 如果play按钮被按下，使用按下亮度
    if play被按下:
        play亮度 = 按下亮度变化(play亮度, True)
    
    # 应用缩放和透明度
    logo缩放后 = pygame.transform.smoothscale(logo原始, logo当前大小)
    logo缩放后.set_alpha(int(logo透明度))
    
    # 应用play按钮的亮度（通过调整颜色）
    play图片 = play原始.copy()
    # 创建一个与play按钮大小相同的Surface用于调整亮度
    brightness_surface = pygame.Surface(play图片.get_size())
    # 设置颜色（亮度值在0-255之间）
    brightness_value = int(255 * play亮度)
    brightness_surface.fill((brightness_value, brightness_value, brightness_value))
    # 使用multiply混合模式调整亮度
    play图片.blit(brightness_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    
    # 绘制一切
    screen.fill("#333333")
    screen.blit(底, 底.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))
    screen.blit(play图片, play图片.get_rect(center=(play屏幕x, play屏幕y)))
    screen.blit(logo缩放后, logo缩放后.get_rect(center=(logo屏幕x, logo屏幕y)))
    
    fps = int(clock.get_fps())
    fps_text = f"FPS: {fps}"
    fps_surface = pygame.font.Font(None, 24).render(fps_text, True, (255, 255, 255))
    screen.blit(fps_surface, (10, 10))  # 在左上角显示
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()