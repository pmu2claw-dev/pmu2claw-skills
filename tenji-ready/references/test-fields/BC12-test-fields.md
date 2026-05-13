# BC1.2 — TenJI 測試欄位版

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/BC12.md`
真實性：`verified-official`

## 測試目標
驗證裝置可正確辨識 SDP / CDP / DCP，並遵循對應電流限制。

## 建議測項欄位
- protocol: `BC1.2`
- port_types:
  - SDP
  - CDP
  - DCP
- detect_sequence:
  1. attach
  2. primary detection
  3. secondary detection (如適用)
  4. port type classify
  5. current draw verify
- electrical_checks:
  - D+ / D- short on DCP
  - DCP short resistance <= `200Ω`
  - VDP_SRC threshold
  - VDAT_REF threshold
- current_limit_checks:
  - SDP current limit
  - CDP current limit
  - DCP current limit up to `1.5A`
- pass_criteria:
  - port classification 正確
  - current draw 不超出對應限制
  - 檢測閾值行為符合預期
- log_keywords:
  - primary detection
  - secondary detection
  - SDP
  - CDP
  - DCP

## TenJI 建議欄位
- Case ID
- Port type simulated
- D+/D- condition
- Expected classification
- Measured classification
- Current limit observed
- Result
- Fail reason
