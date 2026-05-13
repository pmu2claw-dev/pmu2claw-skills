# Apple 2.4A — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/Apple.md`
真實性：`cross-checked`
用途：把 Apple divider-mode charging 測試欄位轉成 TenJI Test Note（B~N 欄）mapping。

## Mapping 原則
- Apple 2.4A 是 **靜態識別**，不是動態協商；不要硬寫成 handshake / packet flow。
- 重點應放在：
  1. attach 後 VBUS 是否正常
  2. D+ / D- 分壓是否落在目標值
  3. sink 是否依 divider mode 放寬到對應電流
  4. 非對應 divider 時是否 fallback
- `D (Symbol)` 必須唯一。
- 若做 attach 後穩定時間量測，可另外加 `_TMU` row，但 Apple 2.4A 主體不是 timing-driven 協議。

## Protocol → TenJI 欄位對應

| Protocol field | TenJI 欄位 | 寫法建議 |
|---|---|---|
| protocol | C (Test_Item) | 固定 `APPLE_2P4A` 或 `APPLE_DIVIDER` |
| attach_default_5v | H / I | attach 後 VBUS 5V |
| D+ voltage | H / J/K/L/M | 量測 D+ 偏壓 |
| D- voltage | H / J/K/L/M | 量測 D- 偏壓 |
| divider mode | I / N | 註明 `2.0/2.0`、`2.0/2.7`、`2.7/2.0`、`2.7/2.7` |
| allowed current | J/K/L/M | 對應 1.0A / 2.1A / 2.4A |
| current unlock behavior | H / I | 寫 sink draw current 或 source current limit 驗證 |
| fallback behavior | I / N | non-matching divider -> normal USB / BC1.2 behavior |
| log_keywords | N | `divider mode / DP bias / DM bias / 2.4A / fallback` |

## 建議 Test Note 骨架

| B | C | D | E | F | G | H | I | J | K | L | M | N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | APPLE_2P4A | APPLE_ATTACH_5V | PWR_USB |  | Wait 5m | JudgeV VBUS 4.75V 5.25V | Attach 後先確認 default 5V VBUS 正常 | 4.75 | 5.00 | 5.25 | V | default state |
| 2 | APPLE_2P4A | APPLE_BIAS_2V_2V | PWR_USB |  | Wait 5m | MeasV DP/DM 0V 3V | 驗證 D+ / D- 提供 2.0V / 2.0V divider mode | 1.9 | 2.0 | 2.1 | V | current target ≈ 1.0A |
| 2 | APPLE_2P4A | APPLE_BIAS_2V_2P7V | PWR_USB |  | Wait 5m | MeasV DP/DM 0V 3V | 驗證 D+ / D- 提供 2.0V / 2.7V divider mode | 1.9 | 2.0 / 2.7 | 2.8 | V | current target ≈ 2.1A |
| 2 | APPLE_2P4A | APPLE_BIAS_2P7V_2V | PWR_USB |  | Wait 5m | MeasV DP/DM 0V 3V | 驗證 D+ / D- 提供 2.7V / 2.0V divider mode | 1.9 | 2.7 / 2.0 | 2.8 | V | current target ≈ 2.1A |
| 2 | APPLE_2P4A | APPLE_BIAS_2P7V_2P7V | PWR_USB |  | Wait 5m | MeasV DP/DM 0V 3V | 驗證 D+ / D- 提供 2.7V / 2.7V divider mode | 2.6 | 2.7 | 2.8 | V | current target ≈ 2.4A |
| 2 | APPLE_2P4A | APPLE_CURR_1A | PWR_USB |  | Run Pattern | JudgeI VBUS 0A 1.1A | 驗證 2.0V / 2.0V 情境下 sink 可放寬至約 1.0A | 0.9 | 1.0 | 1.1 | A | current unlock |
| 2 | APPLE_2P4A | APPLE_CURR_2P1A | PWR_USB |  | Run Pattern | JudgeI VBUS 0A 2.2A | 驗證 2.0V / 2.7V 或 2.7V / 2.0V 情境下 sink 可放寬至約 2.1A | 2.0 | 2.1 | 2.2 | A | current unlock |
| 2 | APPLE_2P4A | APPLE_CURR_2P4A | PWR_USB |  | Run Pattern | JudgeI VBUS 0A 2.5A | 驗證 2.7V / 2.7V 情境下 sink 可放寬至約 2.4A | 2.3 | 2.4 | 2.5 | A | current unlock |
| 2 | APPLE_2P4A | APPLE_FALLBACK_USB | PWR_USB |  | Run Pattern | JudgeI VBUS 0A 0.5A | 非匹配 divider 條件下，不應錯誤放寬到 2.1A / 2.4A | 待補 |  | 0.5 | A | fallback / coexistence |

## 拆項建議
- divider 偏壓驗證與 current unlock 驗證分開
- 若產品要驗向下相容，可另外拆 `Apple 1A / 2.1A / 2.4A` 三組 section
- 若與 BC1.2 / DCP 共存，建議額外加 row 驗證不誤判
