# FCP / SCP — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/FCP.md`
真實性：`cross-checked`
用途：把 Huawei FCP / SCP 測試欄位轉成 TenJI Test Note（B~N 欄）mapping。

## Mapping 原則
- FCP 與 SCP 要拆開寫：**FCP = 類比 D+/D- 階梯**，**SCP = 數位脈衝/封包**。
- `D (Symbol)` 唯一；timing 類測項尾碼補 `_TMU`。
- 低壓大電流 SCP 相關測項需特別記錄線材、熱、current path 條件。

## 建議 Test Note 骨架

| B | C | D | E | F | G | H | I | J | K | L | M | N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | FCP | FCP_ATTACH_5V | PWR_FCP |  | Wait 5m | JudgeV VBUS 4.75V 5.25V | Attach 後先確認 default 5V state | 4.75 | 5.00 | 5.25 | V | default state |
| 2 | FCP | FCP_DETECT_ENTRY | PWR_FCP |  | Run Pattern | MeasV DP 0V 3.6V | 驗證 D+/D- 類比偵測後進入 FCP mode | 待補 |  | 待補 | V | analog detect |
| 2 | FCP | FCP_REQ_9V | PWR_FCP |  | Run Pattern | JudgeV VBUS 8.5V 9.5V | 驗證 FCP 要求 9V 成功 | 8.5 | 9.0 | 9.5 | V | voltage ladder |
| 2 | FCP | FCP_VBUS_TRANS_TMU | PWR_FCP |  | Run Pattern | MeasDelay detect_done VBUS_target | 量測 FCP request 到 VBUS 轉檔 timing | 待補 |  | 待補 | us | timing |
| 2 | SCP | SCP_CAP_QUERY | PWR_SCP |  | Run Pattern | Decode D+/D- digital pulse traffic | 驗證 SCP capability query 封包可成立 | 待補 |  | 待補 | logic | digital negotiation |
| 2 | SCP | SCP_REQ_CURR | PWR_SCP |  | Run Pattern | JudgeI VBUS 0A 6A | 驗證 SCP 可要求目標電流限制 | 待補 | target | 待補 | A | direct-charge current |
| 2 | SCP | SCP_DIRECT_CHARGE | PWR_SCP |  | Wait 10m | JudgeV VBUS 4V 12V | 驗證進入低壓大電流 direct charge 模式 | 待補 |  | 待補 | V | low-V high-I |
| 2 | SCP | SCP_TIMEOUT_RESET | PWR_SCP |  | Run Pattern | JudgeV VBUS 4.75V 5.25V | timeout / digital error 後應回退到安全 5V | 4.75 | 5.00 | 5.25 | V | fallback |

## 拆項建議
- FCP 與 SCP 分成兩個 section
- FCP 側重 default 5V / D+ D- detect / voltage ladder / transition
- SCP 側重 capability query / packet exchange / current request / timeout reset
