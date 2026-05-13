# Legacy D+ / D- Decision Tree

最後更新：2026-04-21

用途：整理 **Apple / BC1.2 / QC / AFC / FCP / UFCS** 在 legacy USB D+ / D- 路徑上的判斷流程、共存邏輯與測試觀點。這份文件的重點不是背規格，而是回答：

1. 插入後先判什麼
2. 哪些協議是類比、哪些是數位
3. 多協議控制器應怎麼切換狀態機
4. debug 時該先懷疑哪一層

---

## 1. 一句話總覽

- **BC1.2**：基礎層，先判 port type（SDP / CDP / DCP）
- **Apple 2.4A**：靜態 divider bias，無動態 negotiation
- **QC / AFC / FCP**：建立在 BC1.2 / DCP 之後的 **類比 D+ / D- 高壓請求**
- **UFCS / SCP**：建立在 D+ / D- 上的 **數位封包/脈衝通訊**
- **PD**：走 CC，不走 D+ / D-；若 PD 成立，通常 legacy D+ / D- 快充流程應抑制或降級

---

## 2. 協議類型分群

### A. 靜態偏壓 / 電阻識別
- Apple 1A / 2.1A / 2.4A
- BC1.2 SDP / CDP / DCP

### B. 類比電壓協商
- QC 2.0 / 3.0
- AFC
- FCP

### C. 數位脈衝 / UART-like 通訊
- UFCS
- Huawei SCP

---

## 3. 高層 decision tree

```text
Cable attach
  -> Check connector family / policy
     -> If USB-C CC / PD path is active and PD contract succeeds
        -> Stay in PD path
        -> Suppress or deprioritize D+ / D- legacy fast-charge negotiation
     -> Else continue legacy D+ / D- path

Legacy D+ / D- path
  -> Check baseline port type / bias condition
     -> If SDP/CDP/DCP behavior detected -> establish BC1.2 baseline
     -> If Apple divider bias detected -> allow Apple current unlock path
     -> If neither stable -> stay at safe 5V / default USB current

If DCP or vendor-specific charger candidate is present
  -> Decide protocol family on D+ / D-
     -> If digital framing / UART-like traffic detected
        -> Try UFCS / SCP state machine
        -> If negotiation succeeds -> enter digital negotiated power mode
        -> If digital negotiation fails -> fallback to analog family or safe 5V
     -> Else if analog ladder / pulse thresholds detected
        -> Try QC / AFC / FCP analog state machine
        -> If voltage request succeeds -> enter requested high-voltage mode
        -> Else fallback to BC1.2 DCP / Apple / safe 5V
     -> Else remain in BC1.2 / Apple legacy charging mode
```

---

## 4. 建議的實作順序（控制器視角）

### Step 0 — 先處理 PD / Type-C 優先權
- 若是 Type-C 系統，先看 CC 上是否已建立 PD contract。
- **原則**：PD 成立時，不要再讓 D+ / D- legacy 快充狀態機亂跑。
- 若是 USB-A 或 A-to-C legacy 場景，才由 D+ / D- 當主路徑。

### Step 1 — 建立 baseline
先回答：這是不是標準 USB、BC1.2、還是 Apple divider？

#### 1A. BC1.2 baseline
- 看 SDP / CDP / DCP
- 若 D+ / D- 短路（<200Ω）或 primary / secondary detection 成立，判進 BC1.2 family
- 這一層常是 QC / AFC / FCP 的前置條件

#### 1B. Apple divider baseline
- 若 D+ / D- 落在固定偏壓（2.0V / 2.0V、2.0V / 2.7V、2.7V / 2.0V、2.7V / 2.7V）
- 則進 Apple current unlock 路徑
- **注意**：Apple 不是動態協商，不會有 request / accept / baud / CRC

### Step 2 — 分流成 analog 或 digital
若不是單純停在 BC1.2 / Apple，而是要進更高功率 legacy fast charge：

#### 2A. 類比家族（QC / AFC / FCP）
特徵：
- D+ / D- 施加特定類比電壓或脈衝
- 請求 5V -> 9V / 12V / 更高檔位
- 常見流程是先 default 5V，再進高壓

適合先試的情境：
- 已確認 DCP baseline
- 看不到明確數位 framing
- 平台主打高壓小電流 legacy 快充

#### 2B. 數位家族（UFCS / SCP）
特徵：
- D+ / D- 上有 serial / pulse-style 封包行為
- 有 capability query / ACK / timeout / retry / reset 概念
- 能做更細緻的 V/I request

適合先試的情境：
- 控制器支援數位 decoder
- 看到 training / packet / digital edge pattern
- 平台要支援 UFCS / direct-charge 類生態

---

## 5. 各協議最短辨識句

### BC1.2
> 先分 SDP / CDP / DCP，是所有 legacy charging 的地板層。

### Apple 2.4A
> 看固定 D+ / D- 偏壓，符合就放寬電流，不做動態 negotiation。

### QC
> 先走 DCP / 0.6V 類 entry，再以 D+ / D- 類比階梯或 pulse 調 VBUS。

### AFC
> 很像 QC 2.0，但 entry timing / 相容細節不同，不能直接等同 QC。

### FCP
> 類似 QC 的 Huawei 類比高壓請求路徑。

### UFCS
> D+ / D- 上跑 UART-like digital negotiation，帶 ACK / timeout / retry。

### SCP
> Huawei 的數位大電流路徑，概念更接近 UFCS 而不是 QC。

---

## 6. 多協議共存原則

### 原則 1：PD 優先於 D+ / D-
- Type-C + PD 成立時，legacy D+ / D- 協議通常不該再主導功率協商。

### 原則 2：先基礎、再快充
- 先確認 baseline（BC1.2 / Apple / safe 5V）
- 再進一步判斷 QC / AFC / FCP / UFCS / SCP

### 原則 3：數位與類比狀態機要分開
- **UFCS / SCP** 不該用 QC / AFC / FCP 的 analog ladder 思路寫
- **QC / AFC / FCP** 也不該被誤判成 serial framed protocol

### 原則 4：fallback 一定要有安全出口
- 協商失敗、timeout、誤碼、detach、invalid request 時
- 都應明確回到 `5V safe state` 或 baseline charging mode

### 原則 5：Apple 不要被誤寫成 BC1.2 DCP
- Apple divider 與 BC1.2 DCP 都可能出現在 D+ / D-
- 但 Apple 的判據是**固定偏壓**，BC1.2 DCP 的判據是**短路 / detection behavior**

---

## 7. debug 順序建議

### Case A：永遠只有 5V
先查：
1. CC / PD 是否先吃掉流程
2. D+ / D- mux 是否接對
3. BC1.2 baseline 有沒有成立
4. Apple divider 或 DCP short 是否真的存在
5. 後續 analog / digital state machine 有沒有被 enable

### Case B：可進 DCP，但上不了 9V / 高功率
先查：
1. 是不是只停在 BC1.2 DCP
2. QC / AFC / FCP entry threshold / timing 是否錯
3. UFCS / SCP decoder 是否沒收進封包
4. Source 是否其實不支援該協議

### Case C：誤判協議、亂切模式
先查：
1. Apple bias 是否被當 DCP / QC entry
2. analog ladder 與 digital decoder 是否同時搶線
3. fallback 條件是否太寬鬆
4. D+ / D- path isolation 是否不足

### Case D：協商成功但不穩
先查：
1. VBUS transition / settle / overshoot
2. cable / load / current path 能力
3. timeout / keep-alive / retry 機制
4. 是否實際進的是別的協議 fallback path

---

## 8. 給 TenJI / 測試規格的拆法建議

若要把這份 decision tree 往下拆成測項，建議分四層：

1. **Baseline layer**
   - BC1.2 SDP / CDP / DCP
   - Apple divider modes

2. **Analog fast-charge layer**
   - QC
   - AFC
   - FCP

3. **Digital fast-charge layer**
   - UFCS
   - SCP

4. **Coexistence / fallback layer**
   - PD vs D+ / D-
   - Apple vs BC1.2
   - analog vs digital family arbitration
   - timeout / error / safe 5V return

---

## 9. 一句話結論

**legacy D+ / D- 世界不是一條協議，而是一個分層路由系統：先判 baseline，再分 analog / digital 家族，最後才進各自的 negotiation。**
