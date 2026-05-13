# UFCS Test Fields Specification

For TenJI test script generation targeting UFCS protocol validation.

## UFCS 核心參數與特性
- **Signaling**: D+ / D-
- **Baud Rate**: Default 115200 bps; official baseline support = 115200 / 57600 / 38400 bps
- **Training**: Each packet starts with Training sequence `0xAA` for baud identification
- **Protocol Type**: Serial digital communication (UART-like) on legacy data lines
- **Data Frame**: 1 start bit + 8 data bits (LSB first) + 1 stop bit
- **Timing**:
  - Inter-frame idle >= 1 bit time
  - Inter-packet idle >= 2 ms
- **Baud tolerance**:
  - TX error <= ±10% vs baseline
  - Within same packet relative error <= ±1%
  - RX must respond within ±15%; > ±20% treated as baud error
- **Retry / fallback**:
  - At least 5 Ping retries without ACK/NCK before switching baud tier
  - If all baud tiers fail, issue hardware reset and exit UFCS mode

## Required Test Fields for TenJI

### 1. Connection & Detection
- `ufcs_attach_detect`: Verify analog mux routes D+/D- to UFCS transceiver instead of USB 2.0 PHY or QC comparator.
- `ufcs_training_detect`: Verify packet begins with Training sequence `0xAA`.
- `ufcs_baud_negotiation`: Verify supported baud tier detection across 115200 / 57600 / 38400 bps.
- `ufcs_baud_switch_after_no_ack`: After >=5 Ping retries without ACK/NCK, verify DUT switches to another supported baud tier.

### 2. Voltage & Current Control
- `ufcs_voltage_request`: Send digital packet to request specific voltage.
- `ufcs_voltage_step`: Verify voltage stepping capability (similar to PPS but over D+/D-).
- `ufcs_current_limit_request`: Send digital packet to request specific current limit.

### 3. State & Protection
- `ufcs_timeout_behavior`: System fallback to safe state / 5V if UFCS communication stops or reset path is invoked.
- `ufcs_crc_ack_behavior`: Verify valid CRC packet gets ACK/NCK response per physical-layer acknowledgment rule.
- `ufcs_baud_error_reject`: Verify receiver does not respond when baud error exceeds official reject range (> ±20%).
- `ufcs_inter_frame_idle`: Verify frame-to-frame idle >= 1 bit time.
- `ufcs_inter_packet_idle`: Verify packet-to-packet idle >= 2 ms.
- `ufcs_usb2_conflict_avoidance`: Verify High-Z state of USB 2.0 PHY during UFCS active state to prevent path contention or damage.
- `ufcs_hw_reset_exit`: Verify DUT issues hardware reset and exits UFCS mode when all supported baud tiers fail.
