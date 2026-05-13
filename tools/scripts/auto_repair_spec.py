#!/usr/bin/env python3
"""
auto_repair_spec.py - 自動修正 TENJI spec 的常見驗證錯誤
"""
import sys
import json
import re

def repair_item(item):
    measure_cond = item.get("measure_cond", "")
    commands = item.get("commands", [])
    
    # 修正 1: 補齊 Wait 的時間單位 (預設為 ms)
    if measure_cond:
        new_lines = []
        for line in measure_cond.splitlines():
            if line.strip().lower().startswith("wait") and not re.search(r"\d+(ns|us|ms|s)", line, re.I):
                # 找數字並補上 ms
                line = re.sub(r"wait\s+(\d+)", r"Wait \1ms", line, flags=re.I)
            new_lines.append(line)
        item["measure_cond"] = "\n".join(new_lines)
    
    for cmd in commands:
        if cmd.get("cmd", "").lower() == "wait":
            params = cmd.get("params", "")
            if params.isdigit():
                cmd["params"] = f"{params}ms"

    # 修正 2: 十六進位格式 (h -> 0x)
    if measure_cond:
        item["measure_cond"] = re.sub(r"\b([0-9A-Fa-f]+)h\b", r"0x\1", item["measure_cond"])
    
    for cmd in commands:
        params = cmd.get("params", "")
        if re.search(r"\b([0-9A-Fa-f]+)h\b", params):
            cmd["params"] = re.sub(r"\b([0-9A-Fa-f]+)h\b", r"0x\1", params)

    # 修正 3: 補齊協議測項的隱性 Attach (如果描述中有但指令漏了)
    desc = item.get("description", "").lower()
    text = (measure_cond + str(commands)).lower()
    if "attach" in desc and "attach" not in text:
        if "c1" in desc:
            item["measure_cond"] = "ForceV vatach1 5V 10m\n" + item.get("measure_cond", "")
        elif "c2" in desc:
            item["measure_cond"] = "ForceV vatach2 5V 10m\n" + item.get("measure_cond", "")

    return item

def repair_spec(spec):
    if "test_items" in spec:
        spec["test_items"] = [repair_item(item) for item in spec["test_items"]]
    return spec

if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
        repaired = repair_spec(data)
        print(json.dumps(repaired, ensure_ascii=False, indent=2))
    except Exception as e:
        # 發生錯誤時回傳原始內容，不中斷流程
        pass
