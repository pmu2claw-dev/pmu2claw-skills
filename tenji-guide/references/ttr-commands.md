# TTR (Test Time Reduction) 平行指令

TTR 系列指令以 `P` 結尾（如 ForceVP, MeasVP），可一次操作**多個 pin**，大幅節省測試時間。

**共同規則：**
- PIN 之間用 `:` 分隔
- PIN 個數必須 >= 2
- 如果所有 pin 的參數值相同，只需填 1 個數值
- 如果各 pin 參數不同，必須用 `:` 分隔，個數與 PIN 數一致

---

## ForceVP — 平行提供定電壓
```
ForceVP  Pin1:PIN2:…:PINN  V1:V2:…:VN  Iclamp1:Iclamp2:…:IclampN
```

## ForceIP — 平行提供定電流
```
ForceIP  Pin1:PIN2:…:PINN  I1:I2:…:IN  Vclamp1:Vclamp2:…:VclampN
```

## MeasVP — 平行量測電壓
```
MeasVP  Pin1:PIN2:…:PINN  VS1:VS2:…:VSN  VE1:VE2:…:VEN  [VAR1:VAR2:…:VARN]
```
- VAR 可選填，不需儲存可省略

## MeasIP — 平行量測電流
```
MeasIP  Pin1:PIN2:…:PINN  IS1:IS2:…:ISN  IE1:IE2:…:IEN  [VAR1:VAR2:…:VARN]
```

## JudgeVP — 平行判斷電壓
```
JudgeVP  Pin1:PIN2:…:PINN  Low1:Low2:…:LowN  High1:High2:…:HighN
```
- Low/High 可用 `NULL` 表示不限

## JudgeDblP — 平行判斷數值
```
JudgeDblP  Low1:Low2:…:LowN  High1:High2:…:HighN
```
- 比對多個 Formula 結果是否各自在規格內

## FormulaP — 平行運算式
```
FormulaP  ::VAR1=polynomial1:VAR2=polynomial2:…:VARN=polynomialN
```
- 每個運算式用 `:` 分隔
- 必須搭配 `::` 開頭

## TuneVP — 平行 Trim 電壓
```
TuneVP  Pin1:PIN2:…:PINN  Target1:Target2:…:TargetN  Low1:Low2:…:LowN  High1:High2:…:HighN
```

---

## 完整範例

```
ForceIP PA6:PA7:PA8:PA9:PA10:PA11:PA12:PA13:PA14:PA15 1m 6
MeasVP PA6:PA7:PA8:PA9:PA10:PA11:PA12:PA13:PA14:PA15 0 5
JudgeVP PA6:PA7:PA8:PA9:PA10:PA11:PA12:PA13:PA14:PA15 0 5
```
→ 提供 PA6~PA15（共 10 pin）定電流 1mA，量測電壓，判定須在 [0V, 5V] 範圍。

```
ForceIP PA2:PA3:PA8:PA9:PA10:PA12:PA13:PA14:PA15 -10u 5
MeasVP PA2:PA3:PA8:PA9:PA10:PA12:PA13:PA14:PA15 0 5
    TRAU2:TRAU3:TRAU8:TRAU9:TRAU10:TRAU12:TRAU13:TRAU14:TRAU15
FormulaP ::RPAU2=(5-TRAU2)/10u:RPAU3=(5-TRAU3)/10u:RPAU8=(5-TRAU8)/10u:RPAU9=(5-TRAU9)/10u:RPAU10=(5-TRAU10)/10u:RPAU12=(5-TRAU12)/10u:RPAU13=(5-TRAU13)/10u:RPAU14=(5-TRAU14)/10u:RPAU15=(5-TRAU15)/10u
JudgeDbl 20 300
```
→ 提供 9 pin 定電流 sink 10uA，量測電壓存入變數，計算各 pin 電阻值，判定 [20, 300]。
