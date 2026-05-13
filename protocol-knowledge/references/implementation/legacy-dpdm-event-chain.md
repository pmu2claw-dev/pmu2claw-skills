# Legacy D+ / D- Event Chain

最後更新：2026-04-21

用途：把 legacy D+ / D- 世界的協議判斷流程，從「decision tree」再往下拆成 **事件鏈（event chain）**。這份文件適合拿來做：
- 測試規格流程圖
- event-chain / state-machine 草稿
- TenJI 測項拆分
- debug checklist

涵蓋協議：`Apple / BC1.2 / QC / AFC / FCP / UFCS / SCP`

---

## 1. Core Event Chain（總鏈）

```text
E0  Cable attach
 -> E1  Check connector / policy
 -> E2  Check CC / PD ownership
 -> E3  If PD active, suppress legacy D+ / D-
 -> E4  Else sample D+ / D- baseline
 -> E5  Classify baseline family
       -> BC1.2
       -> Apple divider
       -> Unknown / safe default
 -> E6  If only baseline supported, stay in baseline charging
 -> E7  If fast-charge candidate exists, choose protocol family
       -> Analog family (QC / AFC / FCP)
       -> Digital family (UFCS / SCP)
 -> E8  Enter protocol-specific negotiation
 -> E9  If accept/success, transition VBUS/current mode
 -> E10 Monitor hold / keep-alive / error / detach
 -> E11 On error or detach, fallback to safe 5V / baseline
```

---

## 2. Stage-by-stage 拆解

## Stage A — Attach / Ownership Layer

### E0. Cable attach
**Trigger**
- USB cable attach / VBUS presence / accessory attach

**Observe**
- VBUS default 5V
- connector family（USB-A / USB-C / A-to-C）
- CC state（若為 Type-C）

**Output**
- 進入 ownership 判定

### E1. Check connector / policy
**Purpose**
- 決定這輪是由 CC/PD 主導，還是 D+ / D- 可參與

**Branch**
- `Type-C + PD capable`
- `Legacy USB-A or A-to-C`
- `USB data port`

### E2. Check CC / PD ownership
**If**
- PD contract 已建立

**Then**
- 事件鏈轉給 PD path
- legacy D+ / D- fast-charge negotiation 應被抑制或降權

**Else**
- 進入 legacy D+ / D- baseline detection

---

## Stage B — Baseline Layer

### E3. Sample D+ / D- baseline
**Measure**
- D+ / D- 電壓
- D+ / D- 是否短路
- primary / secondary detection behavior
- divider bias 是否穩定存在

**Goal**
- 分辨是 BC1.2、Apple divider，還是未知狀態

### E4. BC1.2 classify
**Candidate**
- SDP
- CDP
- DCP

**Evidence**
- D+/D- short
- VDAT / VDP detection behavior
- 是否可同時資料+充電

**Output**
- `BC12_SDP`
- `BC12_CDP`
- `BC12_DCP`

### E5. Apple divider classify
**Candidate modes**
- `2.0V / 2.0V` -> 1A
- `2.0V / 2.7V` -> 2.1A
- `2.7V / 2.0V` -> 2.1A
- `2.7V / 2.7V` -> 2.4A

**Evidence**
- D+ / D- 固定偏壓
- 無 serial frame
- 無 dynamic negotiation

**Output**
- `APPLE_1A`
- `APPLE_2P1A`
- `APPLE_2P4A`

### E6. Unknown / safe baseline
**If**
- 既不是 BC1.2，也不是 Apple divider

**Then**
- 停在 safe 5V / default USB current
- 不應直接亂進高功率模式

---

## Stage C — Fast-charge Family Arbitration

### E7. Decide fast-charge family
**Entry condition**
- baseline 已建立
- controller / source 宣告還可支援更高功率 legacy path

### Branch 1 — Analog family
候選：
- QC
- AFC
- FCP

**Signature**
- D+ / D- 類比電壓階梯
- 脈衝/階梯請求
- 5V -> 9V / 12V transition

### Branch 2 — Digital family
候選：
- UFCS
- SCP

**Signature**
- D+ / D- 上有封包/serial/pulse framing
- 有 ACK/NCK/timeout/retry/reset 概念
- 可查 capability、再 request power

### Arbitration rule
- **先看有沒有 digital framing**
- 有 -> 優先走 UFCS / SCP 類 state machine
- 沒有 -> 再嘗試 QC / AFC / FCP 類 analog family
- 都不成立 -> 回 baseline charging

---

## Stage D — Analog Family Event Chains

## D1. QC Event Chain

```text
QC0  Start from BC1.2 DCP baseline
 -> QC1  Sink drives QC entry pattern (e.g. 0.6V family behavior)
 -> QC2  Source responds / releases DCP short / confirms QC mode
 -> QC3  Sink requests target VBUS by D+ / D- analog ladder
 -> QC4  Source transitions VBUS to 5V / 9V / 12V / continuous mode
 -> QC5  Sink verifies VBUS target reached
 -> QC6  Optional: QC3.0 pulse-based increment/decrement
 -> QC7  Hold state / monitor errors
 -> QC8  On invalid state -> fallback 5V
```

**Debug focus**
- entry threshold
- DCP prerequisite
- D+/D- ladder voltage correctness
- VBUS transition settle

## D2. AFC Event Chain

```text
AFC0  Start from DCP-like / vendor-recognized baseline
 -> AFC1  Sink sends AFC entry behavior on D+ / D-
 -> AFC2  Source identifies AFC rather than QC
 -> AFC3  Sink requests 9V mode
 -> AFC4  Source raises VBUS to AFC target
 -> AFC5  Sink verifies hold stability
 -> AFC6  On mismatch / detach -> fallback 5V
```

**Debug focus**
- 與 QC 的 disambiguation
- entry timing / pulse width
- 9V hold stability

## D3. FCP Event Chain

```text
FCP0  Start from Huawei-compatible analog baseline
 -> FCP1  Sink drives D+ / D- analog request
 -> FCP2  Source recognizes FCP family
 -> FCP3  Sink requests 9V / higher target
 -> FCP4  Source transitions VBUS
 -> FCP5  Sink verifies target and charge continuity
 -> FCP6  On failure -> safe 5V
```

**Debug focus**
- 是否其實誤走 QC
- Huawei-specific threshold / timing
- fallback 是否正常

---

## Stage E — Digital Family Event Chains

## E1. UFCS Event Chain

```text
UFCS0  Start from legacy attach with D+ / D- digital path enabled
 -> UFCS1  Detect / send training or ping behavior
 -> UFCS2  Source replies ACK if UFCS capable
 -> UFCS3  Sink queries source capability
 -> UFCS4  Source returns supported V/I range
 -> UFCS5  Sink requests target voltage/current
 -> UFCS6  Source accepts and adjusts VBUS
 -> UFCS7  Sink monitors response / CRC / timeout / retry
 -> UFCS8  On repeated fail -> hardware reset / return 5V
```

**Debug focus**
- baud / framing
- ACK/NCK presence
- CRC / timeout
- power request acceptance
- digital/analog family arbitration

## E2. SCP Event Chain

```text
SCP0  Start from Huawei digital-charge capable baseline
 -> SCP1  Sink sends digital capability query on D+ / D-
 -> SCP2  Source confirms SCP support
 -> SCP3  Sink requests target voltage/current window
 -> SCP4  Source enters direct-charge-oriented power mode
 -> SCP5  Sink monitors current / cable / thermal path
 -> SCP6  On timeout / invalid response -> fallback safe mode
```

**Debug focus**
- 是否把 SCP 誤當 FCP
- direct-charge current path
- cable / thermal / protection condition

---

## Stage F — Hold / Monitor / Fallback Layer

### F0. Hold state
協商成功後，不代表流程結束，還要持續監看：
- VBUS 是否掉回 5V
- current 是否被 unexpected clamp
- keep-alive / periodic request 是否失敗
- cable / thermal / protection 是否觸發

### F1. Error classes
可分成：
- `baseline error`：BC1.2 / Apple 本身就沒成立
- `entry error`：有 baseline，但進不了 QC/AFC/FCP/UFCS/SCP
- `transition error`：請求成功但 VBUS 沒切到位
- `hold error`：切到位但維持不住
- `coexistence error`：走錯協議、誤判、互搶

### F2. Fallback rule
下列情況應回 safe state：
- detach
- timeout
- CRC / frame error（digital）
- invalid ladder / invalid threshold（analog）
- source reject
- over-current / thermal / protection trip

**Safe fallback target**
- `5V safe state`
- 或 baseline charging mode（例如 BC1.2 DCP / Apple divider）

---

## 3. 給 TenJI / event-chain 引擎的拆法

可直接把上面事件轉成四層 object：

### Layer 1 — Preconditions
- connector type
- PD ownership
- D+ / D- path enable
- source capability mask

### Layer 2 — Events
- attach
- detect
- classify
- request
- accept
- transition
- hold
- fallback

### Layer 3 — Observables
- D+ voltage
- D- voltage
- D+/D- short
- digital frame present
- ACK/NCK
- VBUS target
- current hold

### Layer 4 — Verdicts
- pass
- partial
- fallback
- wrong-family
- unstable
- fail

---

## 4. 最小 event-chain 模板

```text
[Precondition]
  connector / policy / capability
[Baseline]
  BC1.2 or Apple or safe default
[Family Arbitration]
  analog or digital
[Negotiation]
  request -> accept -> transition
[Hold]
  stability / keep-alive / current
[Fallback]
  safe 5V or baseline return
```

---

## 5. 一句話結論

**decision tree 回答「該走哪一條」，event chain 回答「每一條裡面事件怎麼發生、怎麼驗證、哪裡會失敗」。**
