# VOOC / SuperVOOC 快充協議

## 1. 簡介
*   **制定者**: OPPO (包含 OnePlus 的 Dash/Warp Charge, realme 的 Dart/SuperDart)
*   **核心理念**: **低壓大電流直充** (Direct Charge)。將發熱最大的降壓電路 (Buck Converter) 移到充電器端，手機端僅透過 Charge Pump (電荷泵) 將電流直接導入電池，極大地降低了手機充電時的發熱。

## 2. 物理層實作與特徵
*   **通訊媒介**:
    *   **早期 VOOC**: 使用特製的 USB-A 接頭 (7 pin, 增加額外接點) 與特製線材，利用額外的 pin 腳進行通訊。
    *   **後期 SuperVOOC (Type-C)**: 轉移到 Type-C 介面後，通常利用 D+ / D- 或是特定的 Sideband 通道與加密晶片進行握手。
*   **硬體要求**:
    *   **特製線纜**: 必須使用內建驗證晶片且能承載大電流 (如 6.5A 甚至 10A) 的專用線材。若使用普通線材，最高只能輸出普通功率 (如 5V/2A)。
    *   **專用微控制器**: 充電器與手機端都需要特定的 VOOC MCU 進行加密握手與閉環控制 (Closed-loop control)。
*   **控制邏輯**: 手機端的 BMS (Battery Management System) 持續監測電池電壓、溫度與電流，然後透過通訊線路「即時指揮」充電器調整輸出的電壓與電流。

## 3. 封閉性
*   VOOC 是一個高度專有與封閉的生態系統。雖然 OPPO 開放了部分授權給第三方配件商，但核心通訊協定細節並未對外完全公開，這與開放的 USB PD 或 UFCS 形成對比。
