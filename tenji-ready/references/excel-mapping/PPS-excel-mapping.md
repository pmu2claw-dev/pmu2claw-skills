# USB PD PPS — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/PPS.md`
真實性：`verified-official`
用途：把 PPS 測試欄位版轉成可直接落到 TenJI Test Note（B~N 欄）的 mapping。

## Mapping 原則
- 採 TenJI 固定欄位 `B~N`。
- `D (Symbol)` 必須唯一。
- timing / settling 類測項應用 `_TMU` 尾碼。
- APDO 步階與 keep-alive timeout 若規格未完全公開到可直接下 spec，先保留 `待補`，不要硬填。

## Protocol → TenJI 欄位對應

| Protocol field | TenJI 欄位 | 寫法建議 |
|---|---|---|
| protocol | C (Test_Item) | 固定 `USB_PD_PPS` |
| entry_condition | I / N | `PD contract success + Source Capabilities 含 APDO` |
| handshake_sequence | H / I | PPS entry 與 output transition 步驟 |
| key_parameters.voltage_step/current_step | I / N | 記成規格背景或掃描步階說明 |
| timeout_keep_alive | D / J/K/L/M / N | 可拆成 keep-alive timeout timing row |
| voltage_current_checks | H / J/K/L/M | 量測 target 與 actual V/I |
| pass_criteria | I / N | request 後 output 到位、keep-alive 持續有效 |
| log_keywords | N | `APDO / PPS request / keep alive / timeout / reset` |
| APDO range | I / N | 記可請求範圍 |
| Requested voltage/current | J/K/L/M / I | 目標值 + 說明 |
| Measured voltage/current | H / I | 量測動作與觀測 |
| Settling time | D / J/K/L/M | 轉成 `_TMU` row |
| Keep-alive interval | D / J/K/L/M / N | 可用於 timeout 驗證 row |
| Result / Fail reason | N | 執行結果回填 |

## 建議 Test Note 骨架

| B (Bin) | C (Test_Item) | D (Symbol) | E (PWR Sequence) | F (PseudoCode) | G (Wait/Run Pattern) | H (Measure Condition) | I (Description) | J (Min) | K (Typ) | L (Max) | M (Unit) | N (Remarks) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | USB_PD_PPS | PPS_ENTRY | PWR_PD |  | Run Pattern | ForceV VBUS 5V 3A | PD contract 後確認 Source 提供 APDO，Sink 可送出 PPS Request | 待補 |  | 待補 | V | entry_condition: APDO present |
| 2 | USB_PD_PPS | PPS_VOLTAGE_SET | PWR_PD |  | Wait 5m | JudgeV VBUS 4.9V 21V | 驗證 requested PPS voltage 可正確到位 | 待補 | target | 待補 | V | request voltage/current 寫於 description |
| 2 | USB_PD_PPS | PPS_SETTLING_TMU | PWR_PD |  | Run Pattern | MeasDelay Rising CC1:0:3.3:50% VBUS:0:5:50% - PPS_SET_T | 量測 PPS output transition settling time | 待補 |  | 待補 | us | settling time |
| 2 | USB_PD_PPS | PPS_KEEPALIVE_TMU | PWR_PD |  | Wait 10m | MeasDelay Rising CC1:0:3.3:50% VBUS:0:5:50% - PPS_KEEP_T | 驗證 keep-alive interval/timeout 行為 | 待補 |  | 待補 | s | timeout_keep_alive 約 ~10s，容差待補 |
| 2 | USB_PD_PPS | PPS_TIMEOUT_RECOVERY | PWR_PD |  | Run Pattern | MeasV VBUS 0V 21V PPS_RECOV | 停止 keep-alive 後觀測 reset / recovery | 待補 |  | 待補 | V | log: timeout/reset |

## 拆項建議
- 依 APDO 不同區間拆多筆（最低點 / 中段 / 最高點）。
- 電壓與電流限制最好分開 row。
- keep-alive 正常/停止兩種情境分開驗證。
