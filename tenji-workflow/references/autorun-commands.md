# AutoRun 相關指令

## Parameter — 定義元件參數組合

```
Parameter  vinx:V1:V2:V3:V4  voutx_drN:VOUT1_R1:VOUT2_R2:VOUT3_R3  dcff:C1:C2:C3  cout:M1:M2:M3  ind:M1:M2
```

**參數說明：**
- `vinx` — VIN（輸入電壓）的可能值，用 `:` 分開
- `voutx_drN` — VOUT（輸出電壓）+ 分壓電阻值
  - VOUT 電壓與分壓電阻用 `_` 分開
  - 個別資料用 `:` 分開
- `dcff` — Feedforward capacitor 值
- `cout` — COUT 可能值（用數字代表不同 model）
- `ind` — Inductor 可能值（用數字代表不同 model）

**VIN × VOUT 組合規則：**
- **Buck (DC2DC/LDO):** VOUT < VIN
- **Boost:** VOUT >= VIN
- 組合不是直接乘法，需人工處理

**範例：**
```
Parameter vinx:2.6:3.3:4.2:5 voutx_dr1:1_66.5k:1.8_200k:3.3_453k dcff:0:10p:100p cout:0:1:2 ind:0:1
```
→ VIN 4 種、VOUT 3 種、Dcff 3 種、Cout 3 種（需 model）、Ind 2 種（需 model）

---

## Tenji_var — 定義變數

```
Tenji_var  var_name1=value1  var_name2=value2  int_name1=value1  ...
```

**變數命名規則：**
- `var_` 開頭 → 實數型態（float）
- `int_` 開頭 → 整數型態（integer）
- 各變數用**空格**分隔

**範例：**
```
Tenji_var var_vin=2.2 var_vout=1.2 int_cycle=700 int_long=0 int_long_cycle=50 var_long_delay=550ns
```
→ var_vin = 2.2, var_vout = 1.2, int_cycle = 700, int_long_cycle = 50, var_long_delay = 550ns

---

## MeasV_ALL — 量測所有電壓

全面量測指令，一次量測所有相關 pin。

## MeasV_ALL_0A — 零電流量測所有電壓

在零負載條件下量測所有 pin 電壓。

## MeasV_AVG — 平均值電壓量測

```
MeasV_AVG  PIN  VS  VE  VAR  fpwm
```
- fpwm: PWM 頻率，用於計算平均電壓
- 常用於 DC2DC Load Regulation（搭配 LoadReg_dc2dc）

## MeasV_Ripple — Ripple 量測

量測輸出的 ripple 電壓。

## MeasV_Shoot — Shoot 量測

量測 overshoot / undershoot。
