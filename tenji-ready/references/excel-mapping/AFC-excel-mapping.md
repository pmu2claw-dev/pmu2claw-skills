# AFC — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/AFC.md`
真實性：`cross-checked`
用途：把 Samsung AFC 測試欄位轉成 TenJI Test Note（B~N 欄）mapping。

## Mapping 原則
- AFC 與 QC 類似，但**不要直接把 QC row 改名當 AFC**；至少要保留 mode disambiguation 測項。
- `D (Symbol)` 唯一；timing 類補 `_TMU`。

## 建議 Test Note 骨架

| B | C | D | E | F | G | H | I | J | K | L | M | N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | AFC | AFC_ATTACH_5V | PWR_AFC |  | Wait 5m | JudgeV VBUS 4.75V 5.25V | Attach 後先確認 VBUS 為 default 5V | 4.75 | 5.00 | 5.25 | V | default state |
| 2 | AFC | AFC_DETECT_ENTRY | PWR_AFC |  | Run Pattern | MeasV DP 0V 3.6V AFC_DP | 驗證 D+/D- 偵測後進入 AFC mode | 待補 |  | 待補 | V | mode entry |
| 2 | AFC | AFC_REQ_9V | PWR_AFC |  | Run Pattern | JudgeV VBUS 8.5V 9.5V | 驗證 AFC 可要求 9V 檔位並成功轉換 | 8.5 | 9.0 | 9.5 | V | main charging state |
| 2 | AFC | AFC_VBUS_TRANS_TMU | PWR_AFC |  | Run Pattern | MeasDelay detect_done VBUS_9V | 量測 AFC request 到 VBUS 轉 9V 的時間 | 待補 |  | 待補 | us | timing |
| 2 | AFC | AFC_HOLD_9V | PWR_AFC |  | Wait 20m | JudgeV VBUS 8.5V 9.5V | 9V 充電期間應保持穩定，不可頻繁掉回 5V | 8.5 | 9.0 | 9.5 | V | hold stability |
| 2 | AFC | AFC_FALLBACK_5V | PWR_AFC |  | Run Pattern | JudgeV VBUS 4.75V 5.25V | negotiation fail / detach 時應回到 5V | 4.75 | 5.00 | 5.25 | V | fallback |
| 2 | AFC | AFC_QC_DIFF | PWR_AFC |  | Run Pattern | Observe D+/D- entry behavior | 驗證 source / sink 對 AFC 與 QC 2.0 能做正確區分 | 待補 |  | 待補 | logic | disambiguation |
