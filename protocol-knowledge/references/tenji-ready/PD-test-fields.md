# USB PD — TenJI 測試欄位版

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/PD.md`
真實性：`verified-official`

## 測試目標
驗證 Source / Sink 在 USB PD 協商中的能力宣告、請求、轉壓與回應時序是否符合公開標準。

## 建議測項欄位
- protocol: `PD`
- trigger_condition:
  - Type-C attach 完成
  - CC 通道可通訊
  - Source 已送出 Source_Capabilities
- handshake_sequence:
  1. Attach / CC detect
  2. Source_Capabilities
  3. Sink Request
  4. Accept
  5. PS_RDY
  6. 量測輸出穩定
- key_messages:
  - Source_Capabilities
  - Request
  - Accept / Reject / Wait
  - PS_RDY
  - Soft_Reset / Hard_Reset
- voltage_current_range:
  - 依 advertized PDO 實測
  - 需比對 request target 與最終 VBUS
- timing_checks:
  - tSenderResponse
  - tReceiverResponse
  - Request 到 Accept
  - Accept 到 PS_RDY
  - PS_RDY 到 VBUS 穩定
- pass_criteria:
  - Request 與 PDO 能力一致
  - VBUS 最終值落在 target 容許範圍
  - 關鍵回應不超時
  - 異常時 reset/recovery 可觀測
- log_keywords:
  - PDO
  - RDO
  - Accept
  - PS_RDY
  - timeout
  - hard reset

## TenJI 建議欄位
- Case ID
- Source PDO set
- Requested PDO/RDO
- Expected VBUS
- Measured VBUS
- Response time
- Result
- Fail reason

## 備註
- 具體容差仍需後續補 USB-IF compliance / errata 細節。
- 先作為腳本骨架與欄位模板使用。
