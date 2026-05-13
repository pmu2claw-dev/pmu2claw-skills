# TENJI 巨集指令

巨集指令會自動展開成多條基本 Tenji 語法組合。

---

## LoadRegulation — Load Regulation 測試

```
LoadRegulation  VOUT:iLoadA~iLoadB:VOUT_clamp  spec:low:high  wait:wait_time
```

**參數說明：**
- `VOUT` — 待測 pin
- `iLoadA` — 輕載電流
- `iLoadB` — 滿載電流
- `VOUT_clamp` — 抽載時的 clamp 電壓（須大於 VOUT regulated 值）
- `spec:low:high` — 規格值（low = 低標, high = 高標）
- `wait:wait_time` — 等待時間（需帶單位）

**展開結果：**
```
ForceI VOUT iLoadA VOUT_clamp
Wait wait_time
MeasV VOUT NULL NULL VOUT_A
ForceI VOUT iLoadB VOUT_clamp
Wait wait_time
MeasV VOUT NULL NULL VOUT_B
Formula::VLR1=(VOUT_A-VOUT_B)/VOUT_A*100
JudgeDbl low high
```

---

## LineRegulation — Line Regulation 測試

```
LineRegulation  VIN:vinA~vinB  PIN2:iLoad:Vclamp  spec:low:high  wait:wait_time
```

**參數說明：**
- `VIN` — 輸入電壓 pin
- `vinA`, `vinB` — 兩個不同的輸入電壓值
- `PIN2` — VOUT pin
- `iLoad` — 負載電流
- `Vclamp` — 電壓 clamp
- `spec:low:high` — 規格值
- `wait:wait_time` — 等待時間

**展開結果：**
```
ForceV VIN vinA Iclamp
Wait wait_time
ForceI PIN2 iLoad Vclamp
MeasV PIN2 NULL NULL VCC1_C
ForceV VIN vinB Iclamp
Wait wait_time
ForceI PIN2 iLoad Vclamp
MeasV PIN2 NULL NULL VCC1_D
Formula::VLR2=(vinB-vinA)/(VCC1_D-VCC1_C)
JudgeDbl low high
```

---

## LoadReg_dc2dc — DC2DC Load Regulation

```
LoadReg_dc2dc  VOUT:iLoadA~iLoadC~iLoadB:VOUT_clamp  spec:low:high  wait:wait_time  fpwm
```

**參數說明：**
- `VOUT` — 待測 pin
- `iLoadA` — 輕載電流
- `iLoadC` — 中載電流
- `iLoadB` — 滿載電流
- `VOUT_clamp` — clamp 電壓
- `spec:low:high` — 規格值
- `wait:wait_time` — 等待時間
- `fpwm` — PWM 頻率（必填，用於 MeasV_AVG 平均值量測）

**展開結果（使用 MeasV_AVG）：**
```
ForceI VCC1 iLoadA VOUT_clamp
Wait wait_time
MeasV_AVG VCC1 NULL NULL VCC1_A fpwm
ForceI VCC1 iLoadC VOUT_clamp
Wait wait_time
MeasV_AVG VCC1 NULL NULL VCC1_C fpwm
ForceI VCC1 iLoadB VOUT_clamp
Wait wait_time
MeasV_AVG VCC1 NULL NULL VCC1_B fpwm
Formula::VLR1=(VCC1_A-VCC1_B)/VCC1_C*100
JudgeDbl low high
```

---

## CHECK_ACK — I2C ACK 檢查

巨集指令，包含 ForceV + MeasV + JudgeV 的組合，用於確認 I2C 通訊的 ACK 訊號。

**注意：** CHECK_ACK 是 MSB first（FuseTrim 是 LSB first）

---

## FuseTrim — Serial Fuse Trim

2-pin（clk + data）同步輸出的 serial trim 方式。

**注意：** FuseTrim 是 LSB first

---

## Wait_MTP — MTP 專用等待

MTP 測試專用的等待指令。
