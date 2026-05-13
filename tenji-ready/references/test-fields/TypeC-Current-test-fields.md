# USB Type-C Current Advertisement — TenJI 測試欄位版

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/TypeC-Current.md`
真實性：`verified-official`

## 測試目標
驗證未進入 PD 前，Source 經由 CC 腳位 Rp 廣播的預設 / 1.5A / 3.0A 電流能力是否可被正確辨識。

## 建議測項欄位
- protocol: `USB-C Current Advertisement`
- advertised_levels:
  - Default USB Power
  - 1.5A @ 5V
  - 3.0A @ 5V
- attach_sequence:
  1. CC attach detect
  2. Rd present
  3. vRd sample
  4. classify source current capability
  5. verify input current behavior
- electrical_checks:
  - Rd = `5.1kΩ`
  - Rp mapping for default / 1.5A / 3.0A
  - CC voltage threshold bucket
- pass_criteria:
  - advertised level 被正確辨識
  - sink 依能力調整取流
  - 錯誤廣播或閾值模糊時可記錄 fail mode
- log_keywords:
  - CC
  - Rp
  - Rd
  - vRd
  - current advertisement

## TenJI 建議欄位
- Case ID
- Advertised current level
- Rp condition
- Measured CC voltage
- Classified current level
- Allowed current
- Result
- Fail reason
