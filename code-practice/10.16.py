def to_percentage(confidence):
    pct = confidence * 100
    return pct
p1 = to_percentage(0.925)
print(f"第一帧置信度百分比: {p1}%")
p2 = to_percentage(0.81)
print(f"第二帧置信度百分比: {p2}%")


def get_distance(x1, x2):
    dist = abs(x2 - x1)  # abs() 用于求绝对值
    return(dist)          # 错误提示：这里应该用 print 还是 return？

# 调用函数获取距离，并判断是否发生异常跳变（距离 > 50）
d = get_distance(100.0, 165.0)
print(f"计算出的间距为: {d}")

if d > 50.0:
    print("警告：关键点发生异常大幅跳变！")



def calc_frame_score(angle, conf):
    if conf < 0.6:
        return 0
    elif conf >= 0.6 and angle <= 90:
        return 10
    else:
        return 2
frames = [
    {"id": 1, "angle": 85.0, "conf": 0.95},
    {"id": 2, "angle": 110.0, "conf": 0.88},
    {"id": 3, "angle": 78.0, "conf": 0.42},
    {"id": 4, "angle": 82.0, "conf": 0.91}
]

total_score = 0
for item in frames:
    print(f"第{item['id']}帧得分: {calc_frame_score(item['angle'], item['conf'])}")
    total_score += calc_frame_score(item['angle'], item['conf'])
print(f"总得分: {total_score}")
