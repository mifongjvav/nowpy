# catcher_game.py
import pygame
import os
from osu_parser import parse_osu_file
from assets import extract_osz
from sounds import SoundsManager
from utils import osu_x_to_game_x, game_to_screen_pos

# 常量
SCREEN_W, SCREEN_H = 900, 562
JUDGE_LINE_Y = -175  # 游戏坐标（原点在屏幕中心）
JUDGE_LINE_LEN = 900

def run_catcher(osz_path, screen):
    # 解压 .osz（返回临时目录 path, audio_path, bg_path, list_of_osu_paths）
    tmpdir, audio_path, bg_path, osu_paths = extract_osz(osz_path)
    if not audio_path:
        raise FileNotFoundError("在 .osz 中未找到音频文件（wav/mp3）")
    if not osu_paths:
        raise FileNotFoundError("在 .osz 中未找到 .osu 文件")

    # 让用户选择难度（Version 字段）
    print("找到以下难度：")
    for i, p in enumerate(osu_paths):
        print(f"{i}: {os.path.basename(p)}")
    idx = input("请选择难度编号（默认0）：").strip()
    try:
        idx = int(idx)
    except Exception:
        idx = 0
    osu_path = osu_paths[max(0, min(idx, len(osu_paths)-1))]

    # 解析 .osu（返回 hitobjects 列表：{x, time, type}）
    hitobjects = parse_osu_file(osu_path)

    # 初始化 mixer
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    # 预加载随机打击音效（不含 miss.wav）
    sounds = SoundsManager(os.path.join(tmpdir, "sounds") if os.path.isdir(os.path.join(tmpdir,"sounds")) else os.path.join(os.getcwd(),"sounds"))

    # 加载 assets
    try:
        circle_img = pygame.image.load(os.path.join("game","circle.png")).convert_alpha()
    except Exception:
        circle_img = pygame.Surface((48,48), pygame.SRCALPHA)
        pygame.draw.circle(circle_img, (255,200,0), (24,24), 24)
    try:
        catcher_img = pygame.image.load(os.path.join("game","catcher.png")).convert_alpha()
    except Exception:
        catcher_img = pygame.Surface((120,40), pygame.SRCALPHA)
        pygame.draw.rect(catcher_img, (200,50,50), catcher_img.get_rect())

    # 背景
    if bg_path and os.path.exists(bg_path):
        bg_img = pygame.image.load(bg_path).convert()
        bg_img = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))
    else:
        bg_img = pygame.Surface((SCREEN_W, SCREEN_H))
        bg_img.fill((30,30,30))

    # 设置音乐结束事件
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)

    clock = pygame.time.Clock()
    running = True

    # 预处理：把 osu x (0-512) -> game x (-450..450)
    for obj in hitobjects:
        obj['game_x'] = osu_x_to_game_x(obj['x'])

    # 时间控制：为了让音符在到达判定线前就出现，设置 travel_ms（可根据难度改变）
    # 这里简单按难度名字决定（如果没有可选，设为2000ms）
    travel_ms = 2000
    # spawn_time = hit_time - travel_ms
    for obj in hitobjects:
        obj['spawn_time'] = obj['time'] - travel_ms

    # active notes list
    notes = []
    start_ticks = None
    combo = 0

    # 启动播放
    pygame.mixer.music.play()
    start_ticks = pygame.time.get_ticks()

    # 主循环
    while running:
        dt = clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.mixer.music.stop()
                running = False
            if ev.type == MUSIC_END:
                # 音频播完，直接退出（按你的要求）
                pygame.mixer.music.stop()
                running = False

        # current music time in ms (pygame.mixer.music.get_pos returns ms since play)
        music_pos = pygame.mixer.music.get_pos()
        if music_pos < 0:
            # get_pos 有时返回 -1（比如未播放），使用 tick 差值
            music_pos = pygame.time.get_ticks() - start_ticks

        # spawn notes
        while hitobjects and music_pos >= hitobjects[0]['spawn_time']:
            obj = hitobjects.pop(0)
            # note initial y (game coords): spawn at -600 (更上方)，目标到 JUDGE_LINE_Y 在 obj['time']
            spawn_y = -600
            target_y = JUDGE_LINE_Y
            travel_time = obj['time'] - obj['spawn_time']
            vy = (target_y - spawn_y) / (travel_time/1000.0) if travel_time>0 else 300.0
            notes.append({
                'x': obj['game_x'],
                'y': spawn_y,
                'vy': vy,
                'time': obj['time'],
                'hit': False,
            })

        # 更新 notes 位置
        for n in notes:
            n['y'] += n['vy'] * (dt/1000.0)

        # 绘制
        screen.blit(bg_img, (0,0))

        # 把游戏坐标原点映到屏幕中心
        # 判定线（水平，长度 900）
        p1 = game_to_screen_pos(-JUDGE_LINE_LEN/2, JUDGE_LINE_Y, SCREEN_W, SCREEN_H)
        p2 = game_to_screen_pos(JUDGE_LINE_LEN/2, JUDGE_LINE_Y, SCREEN_W, SCREEN_H)
        pygame.draw.line(screen, (255,255,255), p1, p2, 4)
        # 盘子（跟随鼠标）
        mx, my = pygame.mouse.get_pos()
        # 由于原点在屏幕中心，盘子y固定在判定线位置
        catcher_screen_pos = game_to_screen_pos(0, JUDGE_LINE_Y, SCREEN_W, SCREEN_H)
        # 让盘子x跟随鼠标，但映射为游戏坐标[-450,450]再转换回屏幕（以限制不超出判定线）
        # 将鼠标屏幕坐标映射到游戏 x
        catcher_rect = catcher_img.get_rect(center=(mx, catcher_screen_pos[1]))
        screen.blit(catcher_img, catcher_rect)

        # 绘制 notes（并检测碰撞）
        for n in notes[:]:
            sx, sy = game_to_screen_pos(n['x'], n['y'], SCREEN_W, SCREEN_H)
            rect = circle_img.get_rect(center=(sx, sy))
            screen.blit(circle_img, rect)

            # 简单 AABB 碰撞检测：如果 circle 底部/中心接触 catcher_rect 且接近判定线就算 catch
            if rect.colliderect(catcher_rect):
                # 根据坐标系，判定 y 到达判定线的逻辑：为避免时序问题，我用 >= 判断（到达或越过）
                if n['y'] >= JUDGE_LINE_Y - 5:
                    # 命中
                    combo += 1
                    # 根据 n['x'] 做立体声 panning：将游戏 x (-450..450) 归一为 0..1
                    pan = (n['x'] + (JUDGE_LINE_LEN/2)) / JUDGE_LINE_LEN
                    left = max(0.0, min(1.0, 1 - pan))
                    right = max(0.0, min(1.0, pan))
                    sounds.play_hit(left, right)
                    notes.remove(n)
                    continue

            # 如果音符已经越过判定线很远仍未被接（即 y > JUDGE_LINE_Y + 50），视为 Miss
            if n['y'] > JUDGE_LINE_Y + 80:
                # miss：播放 miss.wav（也做声像）
                pan = (n['x'] + (JUDGE_LINE_LEN/2)) / JUDGE_LINE_LEN
                left = max(0.0, min(1.0, 1 - pan))
                right = max(0.0, min(1.0, pan))
                sounds.play_miss(left, right)
                notes.remove(n)
                combo = 0  # 重置连击（示例行为）
                continue

        # 在左上角显示 combo
        font = pygame.font.Font(None, 36)
        surf = font.render(f"Combo: {combo}", True, (255,255,255))
        screen.blit(surf, (10,10))

        pygame.display.flip()

    # 清理临时文件夹（extract_osz 可能在 tmpdir 写了临时文件）
    try:
        import shutil
        if tmpdir and os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)
    except Exception as e:
        print("清理临时目录失败：", e)
