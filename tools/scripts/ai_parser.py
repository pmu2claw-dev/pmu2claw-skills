#!/usr/bin/env python3
"""
TENJI AI Parser
把使用者的自然語言需求，用 LLM 轉成 TENJI Excel spec JSON
"""
import sys
import json
import os
import re
import subprocess
from pathlib import Path

from memory_loader import build_memory_brief

# TENJI 知識庫：按需載入，避免每次全載 ~24KB
SKILL_DIR = Path.home() / ".openclaw/workspace/skills/tenji-guide/references"

# 永遠載入（核心規則，5KB）
_CORE_FILE = "CORE_RULES.md"

# 觸發關鍵字 → 補充載入的檔案
_CONDITIONAL_FILES = {
    "ttr-commands.md":    re.compile(r"\b(ttr|tmu|freq|freqtmu|timing|time|時間|頻率)\b", re.I),
    "macro-commands.md":  re.compile(r"\b(macro|loop|repeat|label|goto|重複|巡迴)\b", re.I),
    "pseudocode-i2c.md":  re.compile(r"\b(i2c|spi|smbus|slave|register|寄存器|I2C)\b", re.I),
    "syntax-commands.md": re.compile(r"\b(ForceV|ForceI|MeasV|MeasI|Judge|UR|Wait|Run)\b", re.I),
    "excel-structure.md": re.compile(r"\b(excel|xlsm|column|欄位|格式|header|頭)\b", re.I),
    "qa-and-rules.md":    re.compile(r"\b(rule|規則|注意|pitfall|錯誤|常見|qa)\b", re.I),
}

def _load_knowledge_for(user_text: str) -> str:
    chunks = []
    core = SKILL_DIR / _CORE_FILE
    if core.exists():
        chunks.append(core.read_text(encoding="utf-8"))
    for fname, pattern in _CONDITIONAL_FILES.items():
        if pattern.search(user_text):
            fpath = SKILL_DIR / fname
            if fpath.exists():
                chunks.append(f"## {fname}\n" + fpath.read_text(encoding="utf-8"))
    return "\n\n".join(chunks)

_SYSTEM_PROMPT_TEMPLATE = """你是 TENJI Test Note 專家，把工程師需求轉成 JSON spec。只輸出純 JSON，不要 markdown。

{knowledge}

輸出格式（精簡示例）：
{{"action":"generate","ic_name":"...","project":"...","notes":"","pinmap":[{{"pin_name":"VIN","type":"PWR","N":"1.7V","O":"1.7V"}}],"power_sequence":{{"PWR_Normal":[{{"pin":"VIN","action":"5V","delay":"1ms"}}]}},"test_items":[{{"name":"IQ_VIN","symbol":"IQ_VIN","pwr_seq":"PWR_Normal","measure_cond":"MeasI VIN 0 50uA","min":"0","max":"50","unit":"uA"}}],"i2c_sequences":[]}}

規則：IQ_/Leak_ ForceV≥pinmap N/O；TMU suffix→頻率；Wait需單位；append→existing excel；只輸出JSON。"""


def _memory_meta_for_request(user_text: str) -> dict:
    try:
        memory_brief = build_memory_brief(user_text, limit=8)
    except Exception:
        memory_brief = {}

    return {
        "memory_brief": memory_brief.get("brief", ""),
        "memory_context_preview": memory_brief.get("context_preview", ""),
        "memory_rules_applied": memory_brief.get("rules_applied", []),
    }


def _build_system_prompt(user_text: str) -> tuple[str, dict]:
    memory_meta = _memory_meta_for_request(user_text)
    knowledge = _load_knowledge_for(user_text)
    prompt = _SYSTEM_PROMPT_TEMPLATE.format(knowledge=knowledge)
    if memory_meta.get("memory_brief"):
        prompt += "\n" + memory_meta["memory_brief"]
    return prompt, memory_meta


def _attach_parser_meta(spec: dict, existing_excel: str = None, fallback_used: bool = False, memory_meta: dict | None = None) -> dict:
    memory_meta = memory_meta or {}
    spec.setdefault("_parser_meta", {})
    spec["_parser_meta"]["fallback_used"] = fallback_used
    spec["_parser_meta"]["existing_excel"] = existing_excel or spec["_parser_meta"].get("existing_excel", "")
    spec["_parser_meta"]["memory_context_preview"] = memory_meta.get("memory_context_preview", "")
    spec["_parser_meta"]["memory_rules_applied"] = memory_meta.get("memory_rules_applied", [])
    spec["_parser_meta"].setdefault("memory_warnings", [])
    return spec

def parse_user_request(user_text: str, existing_excel: str = None) -> dict:
    """
    呼叫 claude CLI 解析使用者需求，回傳 spec dict
    """
    context = f"""使用者需求：{user_text}"""
    if existing_excel:
        context += f"\n\n（附註：使用者提供了現有 Excel 檔案：{existing_excel}，請設定 action=append）"
    system_prompt, memory_meta = _build_system_prompt(user_text)

    # 用 openclaw/claude 的 AI 能力來解析（透過 stdin pipe 給 agent-discordbot 的 AI 子流程）
    # 這裡使用 claude CLI 或 openclaw 內建 AI
    # 方案：直接呼叫 openclaw agent 的 AI endpoint

    # 嘗試使用本機 claude CLI
    try:
        result = subprocess.run(
            ["claude", "--print", "--system", system_prompt, context],
            capture_output=True, text=True, timeout=60
        )
        raw = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # fallback: 使用 openclaw agent CLI
        try:
            result = subprocess.run(
                ["openclaw", "ai", "ask", "--system", system_prompt, context],
                capture_output=True, text=True, timeout=60
            )
            raw = result.stdout.strip()
        except Exception:
            raw = ""

    if not raw:
        # 最後 fallback：回傳基礎模板
        return _minimal_spec(user_text, existing_excel=existing_excel, fallback_used=True, memory_meta=memory_meta)

    # 清理 JSON（有時 LLM 會包 ```json ...```）
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        spec = json.loads(raw)
        return _attach_parser_meta(spec, existing_excel=existing_excel, fallback_used=False, memory_meta=memory_meta)
    except json.JSONDecodeError:
        # 嘗試找 JSON 區塊
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                spec = json.loads(m.group())
                return _attach_parser_meta(spec, existing_excel=existing_excel, fallback_used=False, memory_meta=memory_meta)
            except:
                pass
        return _minimal_spec(user_text, existing_excel=existing_excel, fallback_used=True, memory_meta=memory_meta)

def _minimal_spec(user_text: str, existing_excel: str = None, fallback_used: bool = True, memory_meta: dict | None = None) -> dict:
    """最小化模板，給 fallback 用"""
    return {
        "action": "append" if existing_excel else "generate",
        "ic_name": "Unknown IC",
        "project": "Unknown Project",
        "notes": f"Generated from: {user_text}",
        "pinmap": [
            {"pin_name": "VIN", "type": "PWR", "instrument": "VPSRC", "N": "1.7V", "O": "1.7V"},
            {"pin_name": "VOUT", "type": "PWR", "instrument": "VPSRC", "N": "0V", "O": "0V"},
        ],
        "power_sequence": [
            {"pin": "VIN", "action": "ForceV 1.8V 50mA", "delay": "1ms"}
        ],
        "test_items": [
            {
                "name": "IQ_VIN_Normal",
                "commands": [
                    {"cmd": "ForceV", "pin": "VIN", "params": "1.8V 50mA"},
                    {"cmd": "Wait",   "pin": "",    "params": "1ms"},
                    {"cmd": "MeasI",  "pin": "VIN", "params": "0 100uA"},
                    {"cmd": "JudgeI", "pin": "VIN", "params": "0 50uA"},
                ]
            }
        ],
        "i2c_sequences": [],
        "_parser_meta": {
            "fallback_used": fallback_used,
            "existing_excel": existing_excel or "",
            "memory_context_preview": (memory_meta or {}).get("memory_context_preview", ""),
            "memory_rules_applied": (memory_meta or {}).get("memory_rules_applied", []),
            "memory_warnings": [],
        },
    }

if __name__ == "__main__":
    args = sys.argv[1:]
    existing_excel = None
    if "--existing-excel" in args:
        idx = args.index("--existing-excel")
        if idx + 1 < len(args):
            existing_excel = args[idx + 1]
            del args[idx:idx + 2]
    user_text = " ".join(args) if args else "生成一個基本的 LDO IQ 測試"
    spec = parse_user_request(user_text, existing_excel=existing_excel)
    print(json.dumps(spec, ensure_ascii=False, indent=2))
