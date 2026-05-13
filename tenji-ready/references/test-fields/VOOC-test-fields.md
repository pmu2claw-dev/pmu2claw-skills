# VOOC / SuperVOOC Test Fields Specification

For TenJI test script generation targeting OPPO VOOC / SuperVOOC validation.

## 邊界條件
- VOOC 生態高度封閉；不少細節未公開
- 必須區分：
  - 可公開交叉驗證的高層框架
  - 未公開、不可硬寫的專有握手細節
- 若無官方資料，狀態要標 `partial` 或 `not-public`

## Required Test Fields
- `vooc_attach_default_5v`: 驗證非專用條件下維持一般 5V charging
- `vooc_cable_auth_presence`: 驗證專用線材 / 驗證晶片存在與否對模式切換的影響
- `vooc_mode_entry`: 驗證在專用 charger + cable 條件下進入 VOOC / SuperVOOC 模式
- `vooc_low_voltage_high_current`: 驗證低壓大電流充電行為
- `vooc_fallback_normal_charge`: 非原廠線 / 認證失敗時回退普通充電
- `vooc_thermal_control_path`: 驗證充電過程中控制迴路與熱保護反應
- `vooc_vendor_private_boundary`: 標示不可公開推定的專有握手區塊
