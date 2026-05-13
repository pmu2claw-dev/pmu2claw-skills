# UFCS (Universal Fast Charging Specification) 融合快充標準

## 1. 簡介與版本
*   **全名**: Universal Fast Charging Specification (移動終端融合快速充電技術)
*   **制定組織**: 中國通信標準化協會 (CCSA) / 終端快速充電技術與產業聯盟 (FCA)
*   **核心目標**: 解決不同品牌 (華為、OPPO、vivo、小米) 之間私有協議不互通的問題，提供跨品牌的大功率快充相容性。
*   **版本演進**:
    *   **Phase 1 (2022)**: `T/CCSA 393—2022` (要求), `T/CCSA 394—2022` (測試)。基於 115200bps UART，最高 60W 等級，支援動態電壓調整 (10mV/10mA steps)。
    *   **Phase 2 (2025)**: `T/CCSA 668—2025` (要求)。增加：
        *   **私有身分驗證 (Authentication)**: 允許各廠商在標準之上實作專屬加密認證。

## 2. 物理層 (Physical Layer)
*   **通訊媒介**: 利用 USB 介面的 **D+ / D-** 腳位。
*   **通訊協定**: 半雙工 (Half-Duplex) UART (非同步串列傳輸)。
*   **Baud Rate (波特率)**: 
    *   預設 **115200 bps** (允許誤差)。
    *   Fallback 波特率包含 57600 bps 或 38400 bps (當通訊品質不佳時)。
*   **信號特徵**: 
    *   邏輯高電位 (High) 與低電位 (Low) 的門檻值 (Threshold) 較為特別，部分實測顯示門檻約在 1.2V 附近。
    *   Source 端在發送時需驅動 D+/D-，Sink 端接收；反之亦然。
    *   總輸入阻抗 (Total Input Resistance) 通常小於 200 ohm。
    *   UI (Unit Interval) 對應波特率，例如 115200bps 對應 UI 約 8.68 us。

## 3. 協議層 (Protocol Layer)
*   **架構**: 基於 Request-Response 模型。通常由 Sink (設備) 發起能力查詢與電壓請求，Source (充電器) 回應。
*   **封包結構**: 包含 Sync, Header, Payload (Data), CRC 等欄位。
*   **握手機制 (Handshake)**:
    1.  **Attach**: 設備插入後，等待 USB PD 或其他標準流程走完或失敗。
    2.  **Ping/ACK**: 設備 (Sink) 透過 D+/D- 發送 UFCS Ping 封包，若充電器 (Source) 支援，會回覆 ACK 封包。
    3.  **Capability Discovery**: Sink 查詢 Source 的輸出能力 (電壓/電流範圍)。
    4.  **Power Request**: Sink 發送具體的電壓與電流請求。
    5.  **Power Accept**: Source 確認請求並調整 VBUS 輸出。
*   **錯誤處理**: 支援 NCK (Negative Acknowledge) 與 CRC 錯誤偵測。若連續超時 (Timeout)，則觸發硬體重置 (Hardware Reset)，回到 5V 預設狀態。

## 4. Phase 2 擴充特性 (T/CCSA 668-2025)
*   **Authentication (身分驗證)**: 允許各廠商在標準之上附加專有的加密驗證流程，可能用於解鎖超大功率 (例如 100W+)。
*   **Cable E-Marker**: 讀取特製線纜內的晶片資訊，確認線纜的電流承載能力是否大於 3A/5A。
*   **Role Swap**: 支援雙向供電設備 (如行動電源或手機對充) 之間交換 Source/Sink 角色。

## 5. 與其他協議的共存 (Coexistence)
*   UFCS 規範要求在啟動前，不應干擾現有的 USB PD (走 CC 腳)。
*   如果 CC 腳協商為 PD 模式，D+/D- 的 UFCS 流程通常被抑制或延後。
*   由於 UFCS 與 QC/FCP 都共用 D+/D-，控制器需要有能力在 UART 模式與類比電壓判斷模式之間切換，通常先嘗試 UFCS，失敗才 fallback 到 QC 類比階梯。
