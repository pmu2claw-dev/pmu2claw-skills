# TENJI 語法指令完整列表

## 基本源指令

### ForceV — 提供定電壓
```
ForceV  PIN  Voltage  Iclamp
```
- PIN: DUT pin 名字
- Voltage: 電壓值（可帶單位 V, mV, uV）
- Iclamp: 電流 clamp 值

### ForceI — 提供定電流
```
ForceI  PIN  Current  Vclamp
```
- PIN: DUT pin 名字
- Current: 電流值（可帶單位 A, mA, uA）
- Vclamp: 電壓 clamp 值

---

## 量測指令

### MeasV — 量測電壓
```
MeasV  PIN  VS  VE  [VAR]
```
- PIN: 要量測的 pin
- VS: 量測最低預估值（可帶單位，NULL 表示不指定）
- VE: 量測最高預估值（可帶單位，NULL 表示不指定）
- VAR: （選填）將結果存入變數

### MeasI — 量測電流
```
MeasI  PIN  IS  IE  [VAR]
```
- PIN: 要量測的 pin
- IS: 量測最低預估值
- IE: 量測最高預估值
- VAR: （選填）將結果存入變數

### MeasFreq — 量測頻率
```
MeasFreq  PIN  FS  FE  [VAR]
```

### MeasDuty — 量測 Duty Cycle
```
MeasDuty  PIN  DS  DE  [VAR]
```

### MeasDelay — 量測延遲時間
```
MeasDelay  PIN1  PIN2  DelayS  DelayE  [VAR]
```
- PIN1: 參考 pin
- PIN2: 目標 pin
- 量測 PIN2 相對於 PIN1 的延遲

### MeasDbl — 量測雙精度值
```
MeasDbl  PIN  S  E  [VAR]
```

### MeasCLK — 量測 Clock
```
MeasCLK  PIN  FS  FE  [VAR]
```

---

## 判斷指令

### JudgeV — 判斷電壓
```
JudgeV  PIN  Low  High
```
- Low: spec 低標（NULL 表示不限）
- High: spec 高標（NULL 表示不限）
- 判定量測電壓是否在 [Low, High] 範圍

### JudgeI — 判斷電流
```
JudgeI  PIN  Low  High
```

### JudgeFreq — 判斷頻率
```
JudgeFreq  PIN  Low  High
```

### JudgeDuty — 判斷 Duty Cycle
```
JudgeDuty  PIN  Low  High
```

### JudgeDbl — 判斷數值
```
JudgeDbl  Low  High
```
- 比對前一個 Formula 計算結果是否在範圍內

---

## Trim 指令

### TuneV — Trim 電壓
```
TuneV  PIN  Target  Low  High  [Iclamp]
```
- Target: 目標電壓
- Low/High: 可接受範圍
- Iclamp:（選填）電流 clamp

### TuneI — Trim 電流
```
TuneI  PIN  Target  Low  High  [Vclamp]
```
- Vclamp:（選填）電壓 clamp

### TuneReg — Trim Register
```
TuneReg  REG  Target  Low  High
```

### Tune2Reg — Trim 雙 Register
```
Tune2Reg  REG1  REG2  Target  Low  High
```

### TuneRegV — Trim Register（電壓導向）
```
TuneRegV  PIN  REG  Target  Low  High
```

### TuneRegI — Trim Register（電流導向）
```
TuneRegI  PIN  REG  Target  Low  High
```

### LoadTrimTable — 載入 Trim Table
```
LoadTrimTable  TableName
```

---

## 運算指令

### Formula — 運算式
```
Formula  ::VAR = polynomial
```
- `::` 是必須的符號
- VAR: 變數名（必須唯一）
- polynomial: 由變數與運算子（+, -, *, /）組成的多項式
- 可使用 Meas 存入的變數或之前測項的結果變數

**範例：**
```
Formula ::VLR1=(VCC1_B-VCC1_A)/0.45
Formula ::R_pull_up=(5-V_meas)/10u
```

### Formula_GBY — GBY 專用運算式
```
Formula_GBY  ::VAR = polynomial
```
- 用法同 Formula，專用於 GBY 相關計算

---

## 其他基本指令

### Wait — 等待
```
Wait  time
```
- time: 等待時間（必須帶單位，如 1ms, 10us, 0.5ms）

### RunPattern — 執行 Pattern
```
RunPattern  PatternName
```

### JudgePattern — 判斷 Pattern
```
JudgePattern  PatternName  Expected
```

### UR — 通用暫存器操作
可用於 G 欄與 H 欄。

### CHECK_MTP — MTP 檢查
```
CHECK_MTP  ...
```
- MTP 測試專用檢查指令
