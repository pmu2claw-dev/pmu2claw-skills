# 快充協議物理接口與實作方式 (Physical Interface & Implementation)

本文檔整理各主流快充協議在實體層（Connector, Pins, Signaling Path）的實作方式與電路設計重點，協助測試腳本與硬體開發驗證。重點回答「協議在實體上到底怎麼做」。

## 1. Type-C 接口與核心接腳定義

USB Type-C Connector 共 24 pins，主要用於快充的接腳包含：
- **VBUS (4 pins)**: 電源傳輸主路徑。預設 5V，PD 可協商至最高 20V (PD 3.0) 或 48V (PD 3.1 EPR)。必須具備足夠的電流乘載能力 (3A 或 5A)。實作上，控制器需要控制外部或內建的負載開關 (Load Switch) 或 Buck-Boost 轉換器。
- **GND (4 pins)**: 接地參考。
- **CC1 / CC2 (Configuration Channel)**: 
  - **Attach-Detect**: 偵測裝置是否插入 (透過電壓準位變化)。
  - **Role Detect**: Source 提供 Rp 提升電阻 (區分 1.5A/3.0A 能力)；Sink 提供 Rd (5.1kΩ) 下拉電阻。
  - **Signaling Path**: USB PD 協議的通訊通道，採用 BMC (Biphase Mark Coding) 編碼，半雙工通訊，速率約 300kbps (±10%)，電平在 0V ~ 1.125V (typical) 左右擺動。
- **D+ / D- (DP/DM)**: Legacy USB 2.0 數據線。非 PD 快充協議核心。
  - **D+/D- Dividers**: Apple 2.4A 利用特定電阻分壓 (如 D+/D- 皆 2.7V)。
  - **Voltage Stepping**: QC 2.0/3.0, FCP, AFC 利用在 D+ 施加 0.6V/3.3V，並讀取 D- 的回應來決定電壓。
  - **UART over D+/D-**: UFCS 使用預設 115200bps 的 UART 封包在此腳位上進行通訊。
- **SBU1 / SBU2**: Sideband Use，少數專有快充可能用於輔助通訊。

## 2. 協議實作架構 (Typical Block Diagram)

一個完整的 Type-C 快充 Sink 端 (例如手機或筆電) 實作通常包含以下模組：

1.  **Connector & Front-End Protection**:
    -   **OVP (Over-Voltage Protection)**: Type-C 腳位間距極小。當拔插或線材品質不良時，高達 20V/28V 的 VBUS 極易短路到旁邊僅耐受 3.3V/5V 的 CC 或 SBU 腳。因此，CC/SBU 前端通常需要高壓 OVP 晶片或控制器內建 24V+ 的耐壓能力。
2.  **Protocol / PD Controller (TCPC/TCPM)**:
    -   **PHY Layer**: 包含 BMC 收發器 (Tx/Rx)、CC 腳位的 Rp/Rd 電阻網路切換、D+/D- 的類比多工器與 ADC/DAC (用於舊協議)。
    -   **Protocol Engine**: 處理協議邏輯、狀態機 (State Machine) 與時序控制 (Timers)。
3.  **Power Management / Charger IC**:
    -   負責接收來自 PD Controller 的指令 (I2C/SMBus 等)，調整 Buck-Boost 轉換器的輸出電壓與電流限制，為電池充電。

### D+/D- 類比多工 (Analog Multiplexing) 實作細節
為了讓同一個 Type-C 接口支援 USB 2.0 數據、QC/FCP 類比電壓、以及 UFCS UART，控制器內部必須實作複雜的 **Analog Mux**:
1.  **USB Data Mode**: D+/D- 直接連通到 USB 2.0 PHY 或 AP/PCH，此路徑需具備高頻寬 (480Mbps) 與低寄生電容。
2.  **Legacy Protocol Mode (QC/AFC/FCP)**: Mux 切換到內部的 ADC 與 DAC/Resistor Divider 網路。DAC 在 D+ 施加電壓 (如 0.6V/3.3V)，ADC 持續監聽 D- 的電壓變化。
3.  **UART Mode (UFCS / SCP)**: Mux 切換到內部的 UART 收發器。需要處理 1.2V 的特殊邏輯閾值，與標準 3.3V/1.8V CMOS 邏輯不同。

切換邏輯通常由協議狀態機控制：默認處於 Data/Legacy 狀態，當收到 UFCS Ping 或特定的喚醒信號時，才動態切換 Mux 路徑。


## 3. 各協議物理層實作特徵 (Signal Path Implications)

*   **USB PD**: 
    -   純粹走 CC 腳。
    -   **測試重點**: 驗證 BMC 信號眼圖、GoodCRC 回應時序 (通常要求在 30us 內)、Rx 接收容忍度。
*   **UFCS (Universal Fast Charging Specification)**:
    -   走 D+/D- 腳。
    -   實作上，控制器會將 D+/D- 從 USB 2.0 PHY 切換到內建的 UART 模組。
    -   **測試重點**: 波特率準確度 (115200 bps)、UART frame 格式、設備插拔時 D+/D- 狀態的釋放與重新連接。
*   **QC 2.0 / 3.0 / 舊協議 (FCP/AFC)**:
    -   走 D+/D- 腳的「類比電壓」。
    -   控制器內部會有電阻分壓網路或 DAC 輸出電壓到 D+，並使用比較器或 ADC 讀取 D- 電壓。
    -   **測試重點**: 電壓轉換的穩定時間 (Settling time)、電壓準位的容忍範圍 (如 0.6V threshold 實際上可能是 0.325V ~ 2.0V)。
*   **MediaTek PE (Pump Express)**:
    -   走 **VBUS** 腳。
    -   透過 Sink 端主動調變 VBUS 上的負載電流 (Current Pulsing) 來發送信號，Source 端感測電流變化後調整輸出電壓。
    -   **測試重點**: 電流脈衝的寬度與間隔時序、負載變動對 VBUS 電壓穩定度的影響。

## 4. 多協議共存 (Multi-Protocol Conflict Resolution)

市售充電器與手機為求最大相容性，通常同時支援 PD 與多種舊協議。
-   **優先級 (Priority)**: 業界預設且標準要求的優先級為 **USB PD 絕對優先**。
-   **握手流程**:
    1.  設備插入後，先透過 CC 腳判斷連接狀態與方向。
    2.  Source 廣播 PD Source Capabilities。
    3.  若 Sink 回應並建立 PD 協議，則 **必須** 鎖定在 PD 模式，忽略 D+/D- 上的信號，以避免協議衝突導致電壓亂跳。
    4.  若一段時間內 (通常數秒) CC 腳沒有 PD 通訊或協商失敗，Controller 才會將 D+/D- 腳位連接到舊協議檢測電路，開始輪詢 (Polling) QC/Apple/BC1.2 等協議。

## 5. 多協議共存下的供電優先級 (Precedence of Power Source Usage)
根據 Qualcomm 官方文件 (80-NH008-13 Rev.B verified-official) 以及業界實作慣例，當 Type-C 接口同時連接並辨識到多種供電來源（例如 Type-C Rp 廣播、USB PD、BC1.2 或私有協議）時，裝置端（Sink）應遵循以下優先級（由高至低）來決定最終汲取的功率上限與協議：
1.  **USB Power Delivery (PD)**: 最高優先級，電壓/電流可配置（最高可達 5A 甚至 EPR 的 5A 範圍）。
2.  **USB Type-C Current @ 3.0A**: 透過 CC 腳位上的 Rp = 10kΩ / 0.85kΩ (視電壓而定，或在 5V 下的 3.0A 廣播) 辨識，5V/3A。
3.  **USB Type-C Current @ 1.5A**: 透過 CC 腳位 Rp 廣播，5V/1.5A。
4.  **USB BC 1.2 (DCP/CDP/SDP)**: 最低優先級，5V，最高 1.5A。
*註：QC 或其他基於 D+/D- 的私有協議通常是在確認 PD 不存在或協商失敗後，且在 BC1.2 檢測流程的延伸階段才介入，但其允許的功率/電壓上限會高於基礎的 Type-C Rp 廣播。*
