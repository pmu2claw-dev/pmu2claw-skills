# PPS (Programmable Power Supply)

## 1. 簡介
*   **從屬關係**: USB Power Delivery (PD) 3.0 的一項可選擴展功能。
*   **制定組織**: USB-IF
*   **核心目標**: 取代各家私有的直充協議 (如早期 QC 3.0 階段、或類似直充的方案)。允許受電設備 (Sink) 對供電設備 (Source) 進行**極為精細的輸出電壓與電流限制調整**。

## 2. 規格參數
*   **電壓調整精度**: 20mV (0.02V) / step。
*   **電流調整精度**: 50mA (0.05A) / step。
*   **常見電壓範圍 (APDO)**:
    *   3.3V - 5.9V
    *   3.3V - 11.0V (最常見，用於 25W/45W 快充)
    *   3.3V - 16.0V
    *   3.3V - 21.0V

## 3. 工作機制與握手 (Protocol Logic)
1.  **能力廣播**: 充電器 (Source) 在其 Capabilities 訊息中廣播 APDO (Augmented Power Data Object)，列出其支援的 PPS 電壓範圍與最大電流。
2.  **請求 (Request)**: 手機 (Sink) 根據其電池目前的電壓、溫度、充電狀態 (SOC)，計算出最理想的充電電壓，並向充電器發送請求。
3.  **閉環控制 (Closed-loop)**:
    *   手機成為整個充電系統的「大腦」。
    *   **Keep-Alive 要求**: 在 PPS 模式下，Sink 必須每隔最多 **10 秒** 向 Source 發送一次新的電壓/電流請求 (即使數值沒變)，以維持 PPS 狀態。
    *   **Timeout 保護**: 若 Source 超過 15 秒沒有收到新的請求，為了安全起見，會觸發 Hard Reset，將電壓降回安全的 5V (PD 預設狀態)。

## 4. 物理層含意
*   通訊完全透過 CC 腳位的 BMC 封包進行。
*   這要求充電器內部的 PD Controller 必須能與其後端的 Buck-Boost 轉換器 (或 Flyback 控制器) 緊密配合，透過 I2C/PWM/類比電壓等方式，即時且精準地調整輸出電壓，且不能產生過大的電壓突波 (Overshoot)。
