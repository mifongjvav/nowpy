# osu_parser.py
"""
非常基础的 .osu 解析器：只读取 HitObjects 行并返回 x(time), y, time, type
参考：osu! wiki .osu 文件格式
"""
def parse_osu_file(path):
    hitobjects = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    in_hit = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("["):
            in_hit = (line.lower() == "[hitobjects]")
            continue
        if in_hit:
            # format: x,y,time,type,hitSound,objectParams,extras
            parts = line.split(",")
            if len(parts) < 3:
                continue
            try:
                x = int(parts[0])
                y = int(parts[1])
                time_ms = int(parts[2])
            except ValueError:
                continue
            # type 字段是 int（bit flags）或其他；我们只把所有物件都当作可接物生成
            hitobjects.append({'x': x, 'y': y, 'time': time_ms})
    # 按时间排序
    hitobjects.sort(key=lambda o: o['time'])
    return hitobjects
