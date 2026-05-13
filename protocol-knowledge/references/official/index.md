# 快充協議知識庫 - 官方與標準彙整 (Official Protocols)

此區專注於收集官方/標準組織發布的協議標準、時序規格與握手流程。作為測試腳本的 Golden Reference。

## 主流協議分類

### 1. 國際標準與 USB-IF 系列
*   **[USB PD (Power Delivery)](PD.md)**: 基於 CC 腳的數位通訊協議，支持高達 240W (PD 3.1 EPR)。
*   **[PPS (Programmable Power Supply)](PPS.md)**: USB PD 3.0 的子集，支援電壓/電流微調 (20mV / 50mA steps)。
*   **[BC1.2 (Battery Charging 1.2)](BC12.md)**: 透過 D+/D- 短路或電阻進行識別，最大 1.5A 供電。


### 2. 跨品牌標準
*   **[UFCS (Universal Fast Charging Specification)](UFCS.md)**: 中國融合快充標準，基於 D+/D- UART 通訊 (預設 115200bps)，支援精細的電壓與電流調整。

### 3. 各廠專有協議 (Legacy & Proprietary)
*   **[QC (Quick Charge - Qualcomm)](QC.md)**: 2.0/3.0 依賴 D+/D- 電壓階梯；4.0+ 則相容/轉向 USB PD PPS。
*   **[Apple 2.4A](Apple.md)**: 依賴 D+/D- 的分壓電阻網路 (例如 2.7V/2.7V 為 2.4A)。
*   **[FCP / SCP (Huawei)](FCP.md)**: FCP 類似 QC 的高壓階梯；SCP 專注於低壓大電流直接充電。
*   **[AFC (Samsung)](AFC.md)**: 自適應快充，利用 D+/D- 進行高壓協商。
*   **[VOOC / SuperVOOC (OPPO)](VOOC.md)**: 強調低壓大電流、專用線纜與特製微控制器。
*   **[PE (Pump Express - MediaTek)](PE.md)**: PE 1.0/2.0 利用 VBUS 負載調變 (Current Pulsing) 發送信號，週期長達 ~2.1s。

## 更新與維護狀態
*   最後更新時間：2026-04-16
*   近期維護重點：
    1.  物理層實作 (Physical Interface): 詳見 `../implementation/physical-interface.md`。重點包含 Connector 防護、PD (BMC)、UFCS (UART) 及 Legacy (D+/D- Dividers, VBUS Pulsing) 的實體信號路徑。
    2.  市售晶片參考 (Protocol Chips Benchmark): 詳見 `../benchmark/protocol-chips.md`。涵蓋 TCPC、PD Controller、Charger IC 及 Front-End Protection IC。

### 4. 基礎 Type-C 規範
*   **[Type-C Current](USBC-Current.md)**: 透過 CC 腳位的 Rp/Rd 電阻網路，進行最基礎的 5V/1.5A 或 5V/3.0A 供電廣播。優先級低於 PD，高於 BC1.2。
