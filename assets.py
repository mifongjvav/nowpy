# assets.py
import zipfile
import tempfile
import os

def extract_osz(osz_path):
    """
    解压 .osz 到临时目录，返回 (tmpdir, audio_path, bg_path, list_of_osu_paths)
    如果 .osz 已经是文件夹也支持直接读取。
    """
    if os.path.isdir(osz_path):
        base = osz_path
        tmpdir = None
    else:
        tmpdir = tempfile.mkdtemp(prefix="osz_")
        with zipfile.ZipFile(osz_path, "r") as z:
            z.extractall(tmpdir)
        base = tmpdir

    # 找音频（优先 wav, 然后 mp3）
    audio_path = None
    for root, _, files in os.walk(base):
        for f in files:
            if f.lower().endswith(".wav") or f.lower().endswith(".mp3"):
                audio_path = os.path.join(root, f)
                break
        if audio_path:
            break

    # 背景 bg.jpg
    bg_path = None
    for root, _, files in os.walk(base):
        for f in files:
            if f.lower().endswith("bg.jpg") or f.lower().endswith("background.jpg") or f.lower().endswith(".jpg"):
                # prefer a file explicitly named bg.jpg
                if f.lower() == "bg.jpg":
                    bg_path = os.path.join(root, f)
                    break
                if not bg_path:
                    bg_path = os.path.join(root, f)
        if bg_path:
            break

    # 所有 .osu 文件
    osu_paths = []
    for root, _, files in os.walk(base):
        for f in files:
            if f.lower().endswith(".osu"):
                osu_paths.append(os.path.join(root, f))
    # 按文件名排序（稳定）
    osu_paths.sort()
    return tmpdir, audio_path, bg_path, osu_paths
