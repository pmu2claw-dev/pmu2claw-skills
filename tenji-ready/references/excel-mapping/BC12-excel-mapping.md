# BC1.2 — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/BC12.md`
真實性：`verified-official`
用途：把 BC1.2 測試欄位版轉成可直接落到 TenJI Test Note（B~N 欄）的 mapping。

## Mapping 原則
- 採 TenJI 固定欄位 `B~N`。
- 一個 port type / detection stage 至少一個獨立 row。
- classification 與 current limit 驗證分開寫，較好 debug。

## Protocol → TenJI 欄位對應

| Protocol field | TenJI 欄位 | 寫法建議 |
|---|---|---|
| protocol | C (Test_Item) | 固定 `BC12` |
| port_types | C / D / I | SDP / CDP / DCP 分別展開成 row |
| detect_sequence | H / I | attach → primary detection → secondary detection |
| electrical_checks | I / N | D+/D- short、VDP_SRC、VDAT_REF 條件寫說明 |
| current_limit_checks | J/K/L/M | 依 port type 填 current spec |
| pass_criteria | I / N | classification 正確且 current draw 不超限 |
| log_keywords | N | `primary detection / secondary detection / SDP / CDP / DCP` |
| Port type simulated | I | 實驗情境描述 |
| D+/D- condition | I / N | 模擬條件 |
| Expected/Measured classification | I / N | 預期與量測結果 |
| Current limit observed | H / J/K/L/M | 量測動作與規格 |
| Result / Fail reason | N | 執行結果回填 |

## 建議 Test Note 骨架

| B (Bin) | C (Test_Item) | D (Symbol) | E (PWR Sequence) | F (PseudoCode) | G (Wait/Run Pattern) | H (Measure Condition) | I (Description) | J (Min) | K (Typ) | L (Max) | M (Unit) | N (Remarks) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | BC12 | BC12_SDP_CLASSIFY | PWR_USB |  | Wait 5m | MeasV DP 0V 5V SDP_DP | 驗證 primary detection 後可正確判定 SDP | 待補 |  | 待補 | V | port type=SDP |
| 2 | BC12 | BC12_SDP_ILIM | PWR_USB |  | Run Pattern | JudgeI VBUS 0A 0.5A | 驗證 SDP 模式下 sink current draw 不超出允許限制 | 待補 |  | 0.5 | A | current_limit_checks / pre-enumeration limit 依專案情境回填 |
| 2 | BC12 | BC12_CDP_CLASSIFY | PWR_USB |  | Wait 5m | MeasV DM 0V 5V CDP_DM | 驗證 secondary detection 後可正確判定 CDP | 待補 |  | 待補 | V | port type=CDP |
| 2 | BC12 | BC12_CDP_ILIM | PWR_USB |  | Run Pattern | JudgeI VBUS 0A 1.5A | 驗證 CDP 模式下可提供 charging downstream port 電流能力 | 待補 |  | 1.5 | A | current_limit_checks |
| 2 | BC12 | BC12_DCP_SHORT | PWR_USB |  | Wait 5m | JudgeV DP 0V 0.2V | 驗證 DCP 條件下 D+ / D- short behavior | 0 |  | 0.2 | V | DCP short resistance <= 200Ω |
| 2 | BC12 | BC12_DCP_CLASSIFY | PWR_USB |  | Wait 5m | MeasV DP 0V 5V DCP_DET | 驗證 primary/secondary detection 後可正確落到 DCP 分類 | 待補 |  | 待補 | V | port type=DCP / paired with D+ / D- short behavior |
| 2 | BC12 | BC12_DCP_ILIM | PWR_USB |  | Run Pattern | JudgeI VBUS 0A 1.5A | 驗證 DCP current limit behavior | 待補 |  | 1.5 | A | current_limit_checks |

## 拆項建議
- SDP / CDP / DCP 各自切成 `classification` 與 `current limit` 兩組；其中 DCP 可額外保留 `D+ / D- short` row 作為 electrical prerequisite。
- 若手上儀器可量 D+ / D- 閾值，可另外拆 `VDP_SRC` / `VDAT_REF` threshold rows。
