# Qualcomm Quick Charge (QC) — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/QC.md`
真實性：`partial`
用途：把 QC 測試欄位版轉成可直接落到 TenJI Test Note（B~N 欄）的 mapping，重點是 **開機 / 啟動事件鏈** 要怎麼描述。

## 重要前提
- Qualcomm 官方公開頁可確認 `Quick Charge` 產品線存在與世代演進，但 **QC 2.0 / 3.0 完整通訊規格並未像 USB-IF PD 那樣完整公開**。
- 因此下列內容應分成兩層看：
  - **可公開交叉驗證的高信度框架**：QC 2.0 / 3.0 透過 `D+ / D-` 做電壓協商；QC 4/4+/5 轉向 USB PD / PPS 相容路線。
  - **細節時序 / 特定電壓組合**：目前僅能列為 `partial`，適合用於測試事件描述骨架，但不要假裝是 Qualcomm 官方完整公開 timing spec。

## TenJI 撰寫原則
- Excel 欄位固定採 `B~N`：`Bin / Test_Item / Symbol / PWR Sequence / PseudoCode / Wait/Run Pattern / Measure Condition / Description / Min / Typ / Max / Unit / Remarks`
- `D (Symbol)` 必須唯一。
- timing / delay 類測項若拆成獨立量測，`Symbol` 尾碼要補 `_TMU`。
- **開機事件鏈寫法** 要聚焦在：
  1. 初始供電是否成立
  2. D+ / D- 是否進入 charger-detect / QC-detect 狀態
  3. 是否完成 mode entry
  4. 是否送出 target voltage request
  5. VBUS 是否切到目標檔位並穩定

## 建議的 QC 開機事件鏈（給 TenJI agent 直接引用）

### 通用描述版
`Attach -> VBUS valid 5V -> D+/D- charger detect / QC detect -> enter QC mode -> request target voltage on D+/D- -> source transitions VBUS -> VBUS reaches target and becomes stable`

### 中文工程描述版
`插入後先建立 5V VBUS 預設供電，裝置於 D+ / D- 執行 charger detection 與 QC mode detection；確認進入 QC 模式後，再透過 D+ / D- 電平/脈衝要求目標電壓，最後確認 Source 端將 VBUS 切換到目標檔位並穩定。`

### 若要寫成 Test Note 的 Description
- `確認 attach 後 VBUS 先建立 5V default state，D+ / D- 完成 QC detect，之後再要求 9V/12V/...，並檢查 VBUS transition 與 stable timing。`
- `確認 QC negotiation 不是上電瞬間直接高壓，而是先 default 5V，再經由 D+ / D- 事件鏈進入 requested voltage state。`

## Protocol → TenJI 欄位對應

| Protocol field | TenJI 欄位 | 寫法建議 |
|---|---|---|
| protocol | C (Test_Item) | 固定 `QC`、`QC2`、`QC3` 或依專案規則展開 |
| boot_prerequisite | I / N | 寫 `VBUS default 5V present, D+/D- connected, sink charger detect enabled` |
| attach_event | E / I | `attach`、`VBUS valid`、`default 5V state` |
| detect_sequence | H / I | `charger detect -> QC detect -> mode entry` |
| negotiation_path | H / I / N | `D+ / D- voltage level` 或 `pulse stepping` |
| target_voltage | J / K / L / M | 5V / 9V / 12V / 20V 或連續步進 target |
| transition_timing | D / J / K / L / M | 拆成 `_TMU` row |
| stable_state_check | H / I | 寫 `JudgeV VBUS ...` 或 `MeasV VBUS ...` |
| pass_criteria | I / N | `default 5V -> detect -> request -> target VBUS stable` |
| log_keywords | N | `QC detect / D+ / D- / 5V default / 9V request / VBUS stable / retry / fallback` |

## 建議 Test Note 骨架

| B (Bin) | C (Test_Item) | D (Symbol) | E (PWR Sequence) | F (PseudoCode) | G (Wait/Run Pattern) | H (Measure Condition) | I (Description) | J (Min) | K (Typ) | L (Max) | M (Unit) | N (Remarks) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | QC | QC_ATTACH_5V | PWR_QC |  | Wait 10m | JudgeV VBUS 4.75V 5.25V | Attach 後先確認 Source 以 default 5V 啟動，尚未進入高壓 QC state | 4.75 | 5.00 | 5.25 | V | boot prerequisite / fallback state |
| 2 | QC | QC_DETECT_ENTRY | PWR_QC |  | Run Pattern | MeasV DP 0V 3.6V QC_DP_ENTRY | 驗證裝置於 D+ / D- 執行 QC detect 並進入 mode entry | 待補 |  | 待補 | V | partial: exact vendor thresholds may vary by generation |
| 2 | QC | QC_REQ_9V | PWR_QC |  | Run Pattern | JudgeV VBUS 8.5V 9.5V | 完成 QC detect 後請求 9V，確認 VBUS 轉換至 9V 檔位 | 8.5 | 9.0 | 9.5 | V | request via D+ / D- |
| 2 | QC | QC_REQ_12V | PWR_QC |  | Run Pattern | JudgeV VBUS 11.4V 12.6V | 完成 QC detect 後請求 12V，確認 VBUS 轉換至 12V 檔位 | 11.4 | 12.0 | 12.6 | V | 若產品只支援 9V 可略過 |
| 2 | QC | QC_VBUS_TRANS_TMU | PWR_QC |  | Run Pattern | MeasDelay DP:entry VBUS:9V 50% | 量測 QC request 到 VBUS 到達目標檔位之 transition timing | 待補 |  | 待補 | us | timing row |
| 2 | QC | QC_STABLE_HOLD | PWR_QC |  | Wait 20m | JudgeV VBUS 8.5V 9.5V | VBUS 達目標電壓後應維持穩定，不可振盪或掉回 5V | 8.5 | 9.0 | 9.5 | V | steady state |
| 2 | QC | QC_FALLBACK_5V | PWR_QC |  | Run Pattern | JudgeV VBUS 4.75V 5.25V | negotiation fail / detach / invalid request 時應 fallback 至 5V default state | 4.75 | 5.00 | 5.25 | V | retry / error path |

## TenJI agent 可直接複用的「開機事件鏈」模板

### 模板 A：QC 2.0 固定檔位
`Power-on / attach 後，先確認 VBUS 進入 default 5V。接著觀察 D+ / D- 進行 charger detect 與 QC mode entry。當 sink 完成 QC 偵測後，透過 D+ / D- 要求 9V 或 12V 檔位，再確認 source 端將 VBUS 轉到目標電壓並保持穩定。若 negotiation 失敗，系統應回到 5V default state。`

### 模板 B：QC 3.0 連續步進
`Power-on / attach 後，VBUS 先建立 5V default state。Sink 先經過 QC detect 進入 continuous mode，之後以 D+ / D- pulse / level stepping 調整目標電壓，量測 VBUS 是否依步進方向改變並在目標電壓附近穩定。`

### 模板 C：寫成非常短的事件鏈
`5V default -> QC detect on D+/D- -> voltage request -> VBUS transition -> stable target voltage`

## 測試拆項建議
- **Boot / entry 類**：先驗 `attach -> 5V default -> detect entry`
- **Request 類**：9V / 12V / 20V 各自獨立 row
- **Timing 類**：`entry -> request -> VBUS stable` 拆 `_TMU`
- **Exception 類**：invalid request / timeout / fallback to 5V
- **QC / reliability 補強類**：加入 `overshoot / settle / hold / retry / re-attach / load-step` 等 row，避免只驗「有到電壓」

## 建議追加的 QC 補強測項

| B (Bin) | C (Test_Item) | D (Symbol) | E (PWR Sequence) | F (PseudoCode) | G (Wait/Run Pattern) | H (Measure Condition) | I (Description) | J (Min) | K (Typ) | L (Max) | M (Unit) | N (Remarks) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | QC | QC_9V_OVERSHOOT_TMU | PWR_QC |  | Run Pattern | MeasVPeak VBUS during 5V_to_9V | 量測 5V 切 9V 過程的 VBUS overshoot，確認不超過保護上限 | 待補 |  | 待補 | V | transition quality |
| 2 | QC | QC_9V_SETTLE_TMU | PWR_QC |  | Run Pattern | MeasDelay request_9V VBUS_in_reg 50% | 量測要求 9V 後 VBUS 進入穩定範圍的時間 | 待補 |  | 待補 | us | settle time |
| 2 | QC | QC_9V_HOLD_LOAD | PWR_QC |  | Wait 20m | JudgeV VBUS 8.5V 9.5V | 9V 請求成功後，在負載條件下保持穩定，不可掉回 5V | 8.5 | 9.0 | 9.5 | V | hold / regulation |
| 2 | QC | QC_LOAD_STEP_RECOVERY_TMU | PWR_QC |  | Run Pattern | MeasDelay load_step VBUS_recover 50% | 負載階躍後量測 VBUS recovery time，確認不異常 reset 或長時間跌落 | 待補 |  | 待補 | us | dynamic load response |
| 2 | QC | QC_REATTACH_RECOVERY | PWR_QC |  | Run Pattern | JudgeV VBUS 4.75V 9.5V | detach / re-attach 後應可重新走完 5V default -> QC detect -> target request | 待補 |  | 待補 | V | retry / hot-plug behavior |
| 2 | QC | QC_INVALID_REQ_FALLBACK | PWR_QC |  | Run Pattern | JudgeV VBUS 4.75V 5.25V | invalid request 或 negotiation fail 後，應回到 5V default state | 4.75 | 5.00 | 5.25 | V | exception path |

## 驗證狀態建議
- `Quick Charge brand / generation roadmap` → 可引用 Qualcomm 官方頁，狀態 `partial`
- `QC 2.0 / 3.0 over D+ / D-` → 可公開交叉驗證，狀態 `cross-checked`
- `精確握手 timing / 每一階電平定義` → 若無 Qualcomm 原始公開規範，不要寫成 `verified-official`
