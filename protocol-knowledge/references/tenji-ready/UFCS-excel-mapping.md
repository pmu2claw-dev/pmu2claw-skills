# UFCS — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/UFCS.md`
真實性：`verified-official`
用途：把 UFCS 測試欄位版轉成可直接落到 TenJI Test Note（B~N 欄）的 mapping。

## Mapping 原則
- 採 TenJI 固定欄位 `B~N`：`Bin / Test_Item / Symbol / PWR Sequence / PseudoCode / Wait/Run Pattern / Measure Condition / Description / Min / Typ / Max / Unit / Remarks`
- `D (Symbol)` 必須唯一。
- timing / idle / retry / baud 類測項若拆成獨立量測，`Symbol` 尾碼補 `_TMU`。
- UFCS 明確走 `D+ / D- UART-like` 數位通訊；量測與描述要把 `training / baud / ACK / CRC / retry / fallback` 寫清楚。

## Protocol → TenJI 欄位對應

| Protocol field | TenJI 欄位 | 寫法建議 |
|---|---|---|
| protocol | C (Test_Item) | 固定 `UFCS` |
| attach_detect | I / N | 寫 `D+/D- routed to UFCS transceiver, USB2/QC path isolated` |
| training_sequence | H / I / N | 寫 `0xAA training detect` |
| baud_negotiation | D / H / I / N | 可拆成 `115200 / 57600 / 38400` 驗證 row |
| voltage_request/current_request | H / I / J/K/L/M | 寫 request target 與 VBUS / ILIM 檢查 |
| inter_frame_idle | D / J/K/L/M | 拆 `_TMU` row |
| inter_packet_idle | D / J/K/L/M | 拆 `_TMU` row |
| crc_ack_behavior | H / I / N | valid CRC → ACK/NCK response |
| timeout / retry / hw reset | I / N | `>=5 ping retries`、`all baud fail -> hw reset -> exit UFCS` |
| log_keywords | N | `training 0xAA / ACK / NCK / CRC / baud error / fallback / hw reset` |

## 建議 Test Note 骨架

| B | C | D | E | F | G | H | I | J | K | L | M | N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | UFCS | UFCS_ATTACH_PATH | PWR_LEGACY |  | Wait 5m | Check path isolation on DP/DM | 驗證 attach 後 D+/D- 已切到 UFCS transceiver，而非 USB2 PHY / QC comparator | 待補 |  | 待補 | V | mux / path isolation |
| 2 | UFCS | UFCS_TRAIN_0XAA | PWR_LEGACY |  | Run Pattern | Decode D+/D- serial waveform | 驗證每個封包前可觀測到 training sequence `0xAA` | 待補 |  | 待補 | bit | training detect |
| 2 | UFCS | UFCS_BAUD_115K | PWR_LEGACY |  | Run Pattern | Decode UART-like D+/D- traffic at 115200bps | 驗證預設 baud 115200 bps 可正常建立通訊 |  | 115200 |  | bps | baseline baud |
| 2 | UFCS | UFCS_PKT_IDLE_TMU | PWR_LEGACY |  | Run Pattern | MeasDelay packet_end packet_start | 驗證 inter-packet idle >= 2 ms | 2 |  |  | ms | packet spacing |
| 2 | UFCS | UFCS_FRAME_IDLE_TMU | PWR_LEGACY |  | Run Pattern | Measure bit-to-bit frame spacing | 驗證 inter-frame idle >= 1 bit time | 1 |  |  | bit-time | frame spacing |
| 2 | UFCS | UFCS_VREQ_9V | PWR_LEGACY |  | Run Pattern | JudgeV VBUS 8.5V 9.5V | 透過數位封包要求 9V，確認 Source 接受並將 VBUS 拉到目標範圍 | 8.5 | 9.0 | 9.5 | V | request / accept |
| 2 | UFCS | UFCS_CRC_ACK | PWR_LEGACY |  | Run Pattern | Observe ACK/NCK after valid CRC packet | 驗證 valid CRC packet 有對應 ACK/NCK physical-layer 回應 | 待補 |  | 待補 | logic | crc_ack_behavior |
| 2 | UFCS | UFCS_RETRY_BAUD | PWR_LEGACY |  | Run Pattern | Count ping retries without ACK/NCK | 無 ACK/NCK 時，至少 5 次 Ping retry 後切換 baud tier | 5 |  |  | count | retry / fallback |
| 2 | UFCS | UFCS_HW_RESET_EXIT | PWR_LEGACY |  | Run Pattern | JudgeV VBUS 4.75V 5.25V | 所有支援 baud tier 都失敗後，應觸發 hw reset 並退出 UFCS 模式回到 5V | 4.75 | 5.00 | 5.25 | V | safe fallback |

## 拆項建議
- `baud`：115200 / 57600 / 38400 分開 row
- `power`：電壓請求與電流限制請求分開 row
- `timing`：frame idle / packet idle / response timeout 分開 row
- `exception`：CRC error / baud error / no ACK / all-tier fail / hw reset 分開 row
