# Apple 2.4A Test Fields Specification

For TenJI test script generation targeting Apple divider-mode charging validation.

## Apple 2.4A 核心特性
- 使用 **D+ / D- 靜態分壓** 進行識別
- **無動態協商**、無封包交換、無 baud / CRC / retry 等概念
- Sink 讀取 D+ / D- 固定電壓後，決定是否放寬輸入電流限制
- 典型 Apple divider 模式：
  - `2.0V / 2.0V` → 1.0A
  - `2.0V / 2.7V` → 2.1A
  - `2.7V / 2.0V` → 2.1A
  - `2.7V / 2.7V` → 2.4A

## Required Test Fields

### 1. Divider Detection
- `apple_attach_default_5v`: 驗證 attach 後先有 5V VBUS
- `apple_dp_dm_bias_2v_2v`: 驗證 D+ / D- 可提供 2.0V / 2.0V divider
- `apple_dp_dm_bias_2v_2p7v`: 驗證 D+ / D- 可提供 2.0V / 2.7V divider
- `apple_dp_dm_bias_2p7v_2v`: 驗證 D+ / D- 可提供 2.7V / 2.0V divider
- `apple_dp_dm_bias_2p7v_2p7v`: 驗證 D+ / D- 可提供 2.7V / 2.7V divider

### 2. Current Unlock / Limit
- `apple_1a_current_unlock`: 驗證 2.0V / 2.0V 情境下允許約 1.0A
- `apple_2p1a_current_unlock`: 驗證 2.0V / 2.7V 或 2.7V / 2.0V 情境下允許約 2.1A
- `apple_2p4a_current_unlock`: 驗證 2.7V / 2.7V 情境下允許約 2.4A
- `apple_non_matching_bias_limit`: 驗證不符 divider 條件時不應錯誤放寬到高電流

### 3. Coexistence / Compatibility
- `apple_bc12_coexistence`: 驗證與 BC1.2 / DCP 相容邏輯不衝突
- `apple_legacy_device_compatibility`: 驗證舊款 Apple sink 對 divider mode 可正確識別
- `apple_fallback_normal_usb`: 驗證非 Apple divider 條件下回到一般 USB/BC1.2 行為
