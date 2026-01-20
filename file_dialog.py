# file_dialog.py
from tkinter import Tk, filedialog

def choose_osz_file() -> str | None:
    """
    弹出文件选择框，返回 .osz 路径或 None
    """
    root = Tk()
    root.withdraw()          # 不显示主窗口
    root.attributes("-topmost", True)

    path = filedialog.askopenfilename(
        title="选择 osu! 谱面 (.osz)",
        filetypes=[("osu! Beatmap", "*.osz")],
    )

    root.destroy()
    return path if path else None
