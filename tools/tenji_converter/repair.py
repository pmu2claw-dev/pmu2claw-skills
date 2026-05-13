from __future__ import annotations

from copy import deepcopy
import re
from typing import Any


WAIT_UNIT_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:ns|us|ms|s)", re.IGNORECASE)
HEX_H_RE = re.compile(r"\b([0-9A-Fa-f]+)h\b")


def repair_item(item: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(item)
    measure_cond = str(out.get("measure_cond", ""))
    commands = out.get("commands", [])

    if measure_cond:
        new_lines: list[str] = []
        for line in measure_cond.splitlines():
            if line.strip().lower().startswith("wait") and not WAIT_UNIT_RE.search(line):
                line = re.sub(r"wait\s+([0-9]+(?:\.[0-9]+)?)", r"Wait \1ms", line, flags=re.IGNORECASE)
            line = HEX_H_RE.sub(r"0x\1", line)
            new_lines.append(line)
        out["measure_cond"] = "\n".join(new_lines)

    if isinstance(commands, list):
        for cmd in commands:
            if not isinstance(cmd, dict):
                continue
            cmd_name = str(cmd.get("cmd", "")).lower()
            params = str(cmd.get("params") or cmd.get("value") or "")
            if cmd_name == "wait" and params and not WAIT_UNIT_RE.search(params):
                if re.fullmatch(r"\d+(?:\.\d+)?", params.strip()):
                    params = f"{params.strip()}ms"
            params = HEX_H_RE.sub(r"0x\1", params)
            cmd["params"] = params
            cmd["value"] = params

    desc = str(out.get("description", "")).lower()
    text = (str(out.get("measure_cond", "")) + "\n" + str(out.get("commands", ""))).lower()
    if "attach" in desc and "attach" not in text:
        prefix = ""
        if "c1" in desc:
            prefix = "ForceV vatach1 5V 10m\n"
        elif "c2" in desc:
            prefix = "ForceV vatach2 5V 10m\n"
        if prefix:
            out["measure_cond"] = prefix + str(out.get("measure_cond", ""))

    return out


def repair_spec(spec: dict[str, Any]) -> dict[str, Any]:
    repaired = deepcopy(spec)
    if isinstance(repaired.get("test_items"), list):
        repaired["test_items"] = [repair_item(item) for item in repaired["test_items"]]
    if isinstance(repaired.get("items"), list):
        repaired["items"] = [repair_item(item) for item in repaired["items"]]
    return repaired
