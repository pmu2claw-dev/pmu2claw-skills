# USB PD — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/PD.md`
真實性：`verified-official`
用途：把 protocol 測試欄位版轉成可直接落到 TenJI Test Note（B~N 欄）的 mapping。

## Mapping 原則
- Excel 目標欄位固定採 TenJI `B~N`：`Bin / Test_Item / Symbol / PWR Sequence / PseudoCode / Wait/Run Pattern / Measure Condition / Description / Min / Typ / Max / Unit / Remarks`
- `D (Symbol)` 必須唯一。
- 時間/延遲/頻率類測項若落成獨立量測，`Symbol` 尾碼需補 `_TMU`。
- 本文件先做 **欄位對應與填表骨架**，不假造未公開的實際 timing 容差。

## Protocol → TenJI 欄位對應

| Protocol field | TenJI 欄位 | 寫法建議 |
|---|---|---|
| protocol | C (Test_Item) | 固定用 `USB_PD` 或依專案命名規則展開 |
| trigger_condition | I (Description) / N (Remarks) | 寫成前置條件，例如 `Type-C attach 完成，CC 可通訊，Source 已送出 Source_Capabilities` |
| handshake_sequence | H (Measure Condition) / I (Description) | H 放實際量測步驟；I 可補 sequence 說明 |
| key_messages | I (Description) / N (Remarks) | 記錄 `Source_Capabilities / Request / Accept / PS_RDY / Reset` 觀測重點 |
| voltage_current_range | J/K/L/M | 目標 spec 與單位；若未公開完整容差，可先填 target 值並在 N 標 `待補 compliance limit` |
| timing_checks | D / J/K/L/M / N | timing 測項拆成獨立 row，`D` 用 `_TMU`；J/K/L/M 填時間規格與單位 |
| pass_criteria | I (Description) / N (Remarks) | 寫 pass/fail 判定邏輯 |
| log_keywords | N (Remarks) | 保留除錯關鍵字：`PDO / RDO / Accept / PS_RDY / timeout / hard reset` |
| Source PDO set | I / N | 可寫 advertized 能力摘要 |
| Requested PDO/RDO | I / N | 寫 request target 與 expected sink choice |
| Expected VBUS | J/K/L/M | 規格欄 |
| Measured VBUS | H / I | 量測動作與結果描述 |
| Response time | D / J/K/L/M | 轉成 timing row，例如 `PD_ACCEPT_TMU` |
| Result / Fail reason | N | 留給測試執行結果回填 |

## 建議 Test Note 骨架

| B (Bin) | C (Test_Item) | D (Symbol) | E (PWR Sequence) | F (PseudoCode) | G (Wait/Run Pattern) | H (Measure Condition) | I (Description) | J (Min) | K (Typ) | L (Max) | M (Unit) | N (Remarks) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | USB_PD | PD_CONTRACT_5V | PWR_PD |  | Wait 10m | ForceV VBUS 5V 3A | Attach 後確認 Source_Capabilities 與 Request 可完成 5V contract | 待補 | 5.0 | 待補 | V | trigger: Type-C attach / CC ready |
| 2 | USB_PD | PD_ACCEPT_TMU | PWR_PD |  | Run Pattern | MeasDelay Rising CC1:0:3.3:50% VBUS:0:5:50% - PD_ACCEPT_T | Request 到 Accept/PS_RDY timing 量測骨架 | 待補 |  | 待補 | us | timing_checks: Request→Accept / Accept→PS_RDY |
| 2 | USB_PD | PD_VBUS_STABLE | PWR_PD |  | Wait 5m | JudgeV VBUS 4.75V 5.25V | Request 完成後 VBUS 應落在 target 容許範圍 | 4.75 | 5.00 | 5.25 | V | log: PDO/RDO/PS_RDY |
| 2 | USB_PD | PD_RESET_RECOVERY | PWR_PD |  | Run Pattern | MeasV VBUS 0V 21V VBUS_RST | 異常情境下觀測 Soft Reset / Hard Reset recovery | 待補 |  | 待補 | V | fail reason / timeout / hard reset |

## 拆項建議
- **Contract 類**：依 PDO 電壓檔位拆 row（5V / 9V / 15V / 20V）。
- **Timing 類**：Request→Accept、Accept→PS_RDY、PS_RDY→VBUS stable 各自獨立 row。
- **Exception 類**：Reject / Wait / Soft Reset / Hard Reset recovery 另外成組。

## 備註
- 若手上已有 analyzer log，可再把 `key_messages` 對應到 pattern 名稱或 parser 關鍵字。
- 若之後要進一步自動產生 `.xlsm`，可直接以此 mapping 對應到 B~N 欄。 
