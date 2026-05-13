# AFC Test Fields Specification

For TenJI test script generation targeting Samsung AFC validation.

## AFC 核心特性
- 使用 D+ / D- 進行快充協商
- 典型目標為 9V 高壓檔位
- 底層與 QC 2.0 類似，但識別時序與相容細節不可直接等同

## Required Test Fields
- `afc_attach_default_5v`: 驗證 attach 後先建立 default 5V
- `afc_detect_entry`: 驗證 D+/D- 偵測與 AFC mode entry
- `afc_request_9v`: 驗證 AFC 9V 請求成功
- `afc_vbus_transition_timing`: 驗證 request 後 VBUS transition timing
- `afc_hold_9v`: 驗證進入 9V 後可穩定保持
- `afc_fallback_5v`: negotiation fail / detach / invalid condition 時回到 5V
- `afc_qc_disambiguation`: 驗證同一 source 不把 AFC 誤判成 QC，或反之
