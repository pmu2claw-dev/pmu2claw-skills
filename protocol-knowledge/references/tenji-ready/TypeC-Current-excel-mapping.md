# USB Type-C Current Advertisement — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/TypeC-Current.md`
真實性：`verified-official`
用途：把 Type-C Current Advertisement 測試欄位版轉成可直接落到 TenJI Test Note（B~N 欄）的 mapping。

## Mapping 原則
- 採 TenJI 固定欄位 `B~N`。
- Default / 1.5A / 3.0A 三種 advertised current level 分開成 row。
- CC bucket / allowed current / input current behavior 分開驗證。

## Protocol → TenJI 欄位對應

| Protocol field | TenJI 欄位 | 寫法建議 |
|---|---|---|
| protocol | C (Test_Item) | 固定 `TYPEC_CURRENT` |
| advertised_levels | D / I | Default / 1.5A / 3.0A 分別展開 |
| attach_sequence | H / I | attach / Rd present / vRd sample / classify |
| electrical_checks | I / N | `Rd=5.1kΩ`、Rp mapping、CC threshold bucket |
| pass_criteria | I / N | advertised level 辨識正確、sink 取流正確 |
| log_keywords | N | `CC / Rp / Rd / vRd / current advertisement` |
| Advertised current level | I | 測試情境描述 |
| Rp condition | F / I / N | 若需記錄 fixture/pseudocode 可放 F，否則寫描述 |
| Measured CC voltage | H / J/K/L/M | 量測 vRd |
| Classified current level | I / N | 預期/量測分類 |
| Allowed current | J/K/L/M | 對應可取流上限 |
| Result / Fail reason | N | 執行結果回填 |

## 建議 Test Note 骨架

| B (Bin) | C (Test_Item) | D (Symbol) | E (PWR Sequence) | F (PseudoCode) | G (Wait/Run Pattern) | H (Measure Condition) | I (Description) | J (Min) | K (Typ) | L (Max) | M (Unit) | N (Remarks) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | TYPEC_CURRENT | TYPEC_DEFAULT_CLASSIFY | PWR_TYPEC |  | Wait 5m | MeasV CC1 0V 3V CC1_DEF | 驗證 Default USB Power 廣播下的 CC 電壓 bucket | 待補 |  | 待補 | V | Rd=5.1kΩ |
| 2 | TYPEC_CURRENT | TYPEC_1P5A_CLASSIFY | PWR_TYPEC |  | Wait 5m | MeasV CC1 0V 3V CC1_1P5 | 驗證 1.5A advertisement 辨識 | 待補 |  | 待補 | V | advertised level=1.5A @5V |
| 2 | TYPEC_CURRENT | TYPEC_3A_CLASSIFY | PWR_TYPEC |  | Wait 5m | MeasV CC1 0V 3V CC1_3A | 驗證 3.0A advertisement 辨識 | 待補 |  | 待補 | V | advertised level=3.0A @5V |
| 2 | TYPEC_CURRENT | TYPEC_INPUT_ILIM | PWR_TYPEC |  | Run Pattern | JudgeI VBUS 0A 3.0A | 驗證 sink 依 current advertisement 調整取流 | 待補 |  | 待補 | A | fail mode 可記錄於 remarks |

## 拆項建議
- 若 dual CC 口都要測，CC1 / CC2 各自拆 row。
- 可再加 `TYPEC_RD_CHECK` row 專門驗證 fixture Rd 狀態。
