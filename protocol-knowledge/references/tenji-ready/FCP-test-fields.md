# FCP / SCP Test Fields Specification

For TenJI test script generation targeting Huawei FCP / SCP validation.

## 核心分流
- **FCP**：偏類比 D+/D- 電壓階梯，高壓小電流
- **SCP**：偏 D+/D- 數位脈衝 / 封包交換，低壓大電流直充
- TenJI 寫測項時，不可把 FCP 與 SCP 混成同一套 state machine

## Required Test Fields

### 1. FCP Entry & Voltage Selection
- `fcp_attach_default_5v`: 驗證 attach 後先維持 5V default state
- `fcp_detect_entry`: 驗證 D+/D- 類比偵測後成功進入 FCP 模式
- `fcp_request_9v`: 驗證可請求 9V 檔位
- `fcp_request_12v`: 驗證可請求更高檔位（若產品支援）
- `fcp_vbus_transition_timing`: 驗證 request 後 VBUS transition timing
- `fcp_fallback_5v`: negotiation fail / detach 後應回到 5V

### 2. SCP Digital Negotiation
- `scp_capability_query`: 驗證 sink 可透過 D+/D- 數位序列查詢 source 能力
- `scp_voltage_request`: 驗證數位封包要求特定電壓
- `scp_current_limit_request`: 驗證數位封包要求特定電流限制
- `scp_direct_charge_entry`: 驗證進入低壓大電流模式
- `scp_timeout_reset`: timeout / error 後回退安全狀態
- `scp_packet_ack_behavior`: 驗證封包往返與回應行為

### 3. Shared Protection / Coexistence
- `fcp_scp_mode_separation`: 驗證控制器可區分 FCP 與 SCP 模式
- `fcp_scp_qc_conflict_avoidance`: 驗證 D+/D- 共用時不誤觸發 QC/FCP/SCP 其他模式
- `fcp_scp_cable_current_path`: 驗證大電流模式下線材與 path 條件符合預期
