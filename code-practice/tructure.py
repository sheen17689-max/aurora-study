raw_name = "    right_wrist_point      "

clean_name = raw_name.strip()
clean_name = clean_name.replace("_point", "")
clean_name = clean_name.upper()
print("标准化名称:", clean_name)

front_name = clean_name[:5]
print("前缀:", front_name)


record = "  Squat,86.0  "

# 错误 1：没有把 strip() 的结果重新赋给 record
record = record.strip()

items = record.split(",")
action_name = items[0]
angle_val = float(items[1])

# 错误 2：items[1] 是字符串 "86.0  "，不能直接和 90.0 比大小
if angle_val <= 90.0:
    print(f"动作: {action_name}, 角度: {angle_val}° -> 达标")


sensor_logs = [
    "Nose:320.0:0.95",
    "Left_Ankle:280.5:0.42",
    "Right_Knee:265.0:0.91"
]

for log in sensor_logs:
    parts = log.split(":")
    name = parts[0]
    x = float(parts[1])
    confidence = float(parts[2])
    if confidence >=0.8:
        print(f"有效关键点: {name}, X坐标: {x}, 置信度: {confidence}")
    else:
        print(f"低置信度已忽略: {name}({confidence})")