# utils.py
def osu_x_to_game_x(x, osu_width=512, game_len=900):
    """
    osu x in [0, osu_width] -> game x in [-game_len/2, game_len/2]
    """
    norm = x / osu_width
    return norm * game_len - game_len/2

def game_to_screen_pos(gx, gy, screen_w, screen_h):
    """
    游戏坐标原点在屏幕中心，y 向下为正（与本项目的约定）
    转成屏幕坐标（左上角为 (0,0)）
    注意：在原始 Main.py 中的转换是 screen_y = center_y - game_y（因此 game_y 的正方向为上），
    这里我们采用常规的：game y 向下为正 -> screen_y = center_y + gy
    为了契合你要求的判定线 y = -175（使用负值表示位于 center 下方），我使用：
    screen_y = center_y - gy
    这样保持与用户描述一致。
    """
    cx = screen_w // 2
    cy = screen_h // 2
    sx = int(cx + gx)
    sy = int(cy - gy)
    return (sx, sy)
