# VOOC / SuperVOOC — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/VOOC.md`
真實性：`partial`
用途：把 VOOC / SuperVOOC 測試欄位轉成 TenJI Test Note（B~N 欄）mapping，同時保留封閉協議的資訊邊界。

## Mapping 原則
- 只寫**可驗證的行為層**：專用 charger / cable / 認證存在與否、是否進入低壓大電流、失敗時如何 fallback。
- 不編造未公開的精確封包內容或加密握手細節。
- `D (Symbol)` 唯一；若做 mode transition timing，尾碼補 `_TMU`。

## 建議 Test Note 骨架

| B | C | D | E | F | G | H | I | J | K | L | M | N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | VOOC | VOOC_DEFAULT_5V | PWR_VOOC |  | Wait 5m | JudgeV VBUS 4.75V 5.25V | 非專用條件下，裝置應維持一般 5V charging | 4.75 | 5.00 | 5.25 | V | normal charge fallback |
| 2 | VOOC | VOOC_CABLE_AUTH | PWR_VOOC |  | Run Pattern | Check charger/cable identity path | 驗證專用線材 / 認證條件存在時才允許進入 VOOC 模式 | 待補 |  | 待補 | logic | vendor-auth boundary |
| 2 | VOOC | VOOC_MODE_ENTRY | PWR_VOOC |  | Run Pattern | Observe transition to proprietary fast-charge state | 驗證專用 charger + cable 下可進入 VOOC / SuperVOOC 模式 | 待補 |  | 待補 | state | proprietary mode entry |
| 2 | VOOC | VOOC_LOWV_HIGHI | PWR_VOOC |  | Wait 10m | JudgeI VBUS 0A 10A | 驗證低壓大電流 charging 行為 | 待補 | target | 待補 | A | direct-charge style |
| 2 | VOOC | VOOC_ENTRY_TMU | PWR_VOOC |  | Run Pattern | MeasDelay auth_ok fast_charge_state | 量測認證成立到 fast charge state 的轉換時間 | 待補 |  | 待補 | ms | partial |
| 2 | VOOC | VOOC_FALLBACK_5V | PWR_VOOC |  | Run Pattern | JudgeV VBUS 4.75V 5.25V | 非原廠線 / 認證失敗 / 異常時回退普通 5V charging | 4.75 | 5.00 | 5.25 | V | safe fallback |
