# USB PD (Power Delivery) 快充協議

## 1. 簡介與版本演進
*   **制定組織**: USB-IF
*   **核心目標**: 建立一套標準化、高功率、雙向的數位通訊供電協議，取代所有私有協議。
*   **版本歷史**:
    *   **PD 1.0**: 走 VBUS 上的 FSK 通訊 (已淘汰)。
    *   **PD 2.0**: 轉移到 Type-C 的 CC 腳，採用 BMC 編碼，最高 100W (20V/5A)。
    *   **PD 3.0**: 增加更多訊息類型 (電池狀態、製造商資訊、快速角色切換 FRS)。加入 **PPS (Programmable Power Supply)** 支援。
    *   **PD 3.1**: 劃分出 SPR (Standard Power Range, ≤100W) 與 **EPR (Extended Power Range, 140W/180W/240W)**，增加 28V, 36V, 48V 固定電壓檔位與 AVS (Adjustable Voltage Supply)。
    *   *(目前最新參考版本為 PD 3.2)*

## 2. 物理層 (Physical Layer)
*   **通訊媒介**: Type-C 接口的 **CC1 或 CC2** 腳位 (根據插入方向決定)。
*   **編碼方式**: BMC (Biphase Mark Coding)。這是一種自同步的曼徹斯特編碼變體。
*   **傳輸速率**: 300 kbps (±10%)。半雙工通訊。
*   **訊號特徵**: 訊號電壓擺動幅值典型約為 1.125V。

## 3. 協議架構與訊息
PD 訊息架構包含 Preamble, SOP (Start of Packet), Message Header, Data Objects (PDOs), CRC, EOP。
*   **Source Capabilities**: 供電端廣播其能力 (如 5V/3A, 9V/3A, 20V/5A 等 PDO)。
*   **Request**: 受電端請求特定的 PDO 索引與所需的電流。
*   **Accept / Reject**: 供電端接受或拒絕請求。
*   **PS_RDY**: 供電端調整電壓完畢，通知受電端電源已穩定，可以使用。
*   **GoodCRC**: 硬體層級的確認機制，接收方在收到封包後必須在 ~30us 內回覆 GoodCRC，否則發送方會重傳。

## 4. 關鍵機制 (Key Mechanisms)
*   **PR_Swap (Power Role Swap)**: 允許 Source 與 Sink 在不斷開實體連接的情況下交換供電角色 (如行動電源與手機互充)。
*   **DR_Swap (Data Role Swap)**: 允許 DFP (Host) 與 UFP (Device) 交換數據角色。
*   **VCONN**: 提供給 Type-C 線纜內 E-Marker 晶片的電源 (5V, 通常由未作為通訊用的另一個 CC 腳提供)。當電流需求 >3A 或進入 EPR 模式時，必須讀取線纜的 E-Marker 確認其承載能力。
