# Tenji Excel 結構說明

Tenji Excel 包含 7 個 sheet，每個 sheet 有不同用途。

## 1. Test Note（主要工作區）

測試項目清單，所有測試定義都寫在這裡。

**重要欄位：**
- **D 欄** — 測項名字（必須唯一，不能與其他測項同名）
- **F 欄** — Pin name / 條件 / 註解
  - F0: I2C slave address（如果有 I2C）
  - F 欄可加註解（`//` 開頭）
- **G 欄** — 主要指令參數
- **H 欄** — 指令名稱（ForceV, MeasV, JudgeV 等）
- **P/Q/R/S 欄** — 與 Leakage 測項 1.1 倍相關

**命名規則：**
- 量測時間的測項 → 名稱必須用 `_TMU` 結尾
- `PWR_OS` → 只能用於 Open Short test
- `IQ_` 或 `Leak_` 開頭 → ForceV 電壓不能小於 PinMap N/O 欄所列電壓

## 2. PinMap

DUT pin 的對應表，定義所有 pin 的名稱與屬性。

**重要欄位：**
- Pin name
- N 欄 / O 欄 — 電壓限制值（影響 IQ_/Leak_ 測項的自動檢查）

## 3. Power Sequence

上電順序定義，指定 DUT 各 power pin 的上電次序。

## 4. Pseudo Code

I2C / SWD 等 command list 的巨集定義。將常用的 command sequence 包裝成巨集，提升可讀性。

## 5. LUT（Look Up Table）

查找表，供 Trim 等功能使用。

## 6. Pattern

數位 pattern 定義，用於 RunPattern / JudgePattern 指令。

**特殊指令：**
- `SET_LEVEL` — 設定 pattern 的電壓 level
- 支援 `LOOP` 方式生成重複 pattern

## 7. Schematic

電路圖參考，作為測試設計的依據。

---

## Excel 模板位置

```
Y:\CAD\Public\Bin\Tenji_DOC\專案名稱_內碼名稱_外碼名稱_TenjiV2.1_R0.1.xlsm
```
