# USB PD PPS — TenJI 測試欄位版

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/PPS.md`
真實性：`verified-official`

## 測試目標
驗證 PPS 模式下可程式化調壓/限流請求、逾時保活與輸出穩定性。

## 建議測項欄位
- protocol: `PPS`
- entry_condition:
  - PD 協商成功
  - Source Capabilities 含 APDO
- handshake_sequence:
  1. PD attach
  2. Source_Capabilities with APDO
  3. Sink PPS Request
  4. Accept
  5. PS_RDY / output transition
  6. periodic keep-alive/status
- key_parameters:
  - voltage_step: `20mV`
  - current_step: `50mA`
  - timeout_keep_alive: `~10s` (待進一步確認實作容差)
- voltage_current_checks:
  - target voltage
  - actual voltage
  - current limit behavior
  - transition settling time
- pass_criteria:
  - APDO 存在且可被請求
  - request 後輸出能到位
  - keep-alive 未中斷時不掉線
  - 停止 keep-alive 後 reset/recovery 行為可觀測
- log_keywords:
  - APDO
  - PPS request
  - keep alive
  - timeout
  - reset

## TenJI 建議欄位
- Case ID
- APDO range
- Requested voltage/current
- Measured voltage/current
- Settling time
- Keep-alive interval
- Result
- Fail reason
