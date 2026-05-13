# TENJI Guide Skill

> TENJI (TEst Note Jason Interpreter) — Fitipower 自動化驗證及測試程式產生器使用指南

## Description

協助使用者撰寫、理解、除錯 TENJI Excel 測試定義，以及執行 Tenji2uvm 轉換流程。涵蓋所有 TENJI 語法指令、Excel sheet 結構、Workstation simulation 流程。

**Use when:** 使用者詢問 TENJI 語法、指令用法、Excel 填寫方式、Tenji2uvm 流程、simulation 設定、測試程式撰寫、或任何與 TENJI 使用手冊相關的問題。

**NOT for:** 非 Fitipower TENJI 相關的一般 IC 測試問題。

## Prerequisites

- TENJI 使用手冊 REV 0.2.11（本 skill 基於此版本）
- TenjiC_rev0.1.exe（PC 端轉檔工具）
- Workstation 端需有 UVM 環境（icfb + spectreX）

## References

詳細指令語法與範例請查閱：
- `references/excel-structure.md` — Tenji Excel 7 個 sheet 的結構說明
- `references/syntax-commands.md` — 完整語法指令列表與格式
- `references/ttr-commands.md` — TTR (Test Time Reduction) 平行指令
- `references/macro-commands.md` — 巨集指令（LoadRegulation, LineRegulation, CHECK_ACK 等）
- `references/pseudocode-i2c.md` — PseudoCode / I2C 相關指令
- `references/autorun-commands.md` — AutoRun 相關指令（Parameter, Tenji_var, MeasV_ALL 等）
- `references/tenji2uvm-flow.md` — Tenji2uvm 完整流程（PC 端 + Workstation 端）
- `references/qa-and-rules.md` — Q&A、常見規則、注意事項

## Workflow

1. 先確認使用者的問題類型（語法查詢 / Excel 填寫 / 流程問題 / 除錯）
2. 根據問題類型，查閱對應的 reference 檔案
3. 用繁體中文回答，提供具體格式與範例
4. 對於語法問題，務必列出完整格式、參數說明、範例

## Key Rules

**欄位定義（以 CORE_RULES.md 為準）：**
- Col B=Bin, C=Test_Item, D=Symbol(唯一), E=PWR Sequence
- Col F=PseudoCode(I2C/SWD, 7-bit Slave Address), G=Wait/Run Pattern
- Col H=Measure Condition（核心指令，測項的詳細步驟）
- Col I=Description, J/K/L=Min/Typ/Max, M=Unit, N=Remarks

**核心規則：**
- 所有測項從 Row #3 開始填寫
- Col D (Symbol) 必須唯一，嚴禁重複
- 所有 pin name 必須與 PinMap sheet 定義一致
- 量測時間/頻率/Duty 的測項名稱 → Col D 必須用 `_TMU` 結尾
- `PWR_OS` 只能用於 Open Short test
- IQ_ 或 Leak_ 開頭的 ForceV 電壓不能小於 PinMap N/O 欄所列電壓
- 16 進位強制 `0x` 開頭，嚴禁 `10h` 寫法
- Col H 多步測試 → 儲存格內換行 (Alt+Enter)
- TTR 指令（xxxP 系列）用 `:` 分隔多 pin，一次操作多個 pin 節省測試時間
- TuneV/TuneI 下一行必須配合 Judge 指令作為中斷條件
- Formula 使用 `::` 開頭符號，變數名必須唯一
- PseudoCode 支援部分 bit 操作（如 `0x81:3~0`），F 欄支援 `//` 註解
- FuseTrim 是 LSB first，CHECK_ACK 是 MSB first
