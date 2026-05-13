# Official Protocol Specifications

此目錄包含各主要快充協議的官方技術規範與實作細節，主要作為測試腳本、硬體驗證與系統架構設計的 Golden Reference。

## 內容索引

### USB 標準系列
*   `PD.md`: USB Power Delivery (涵蓋 PD 2.0 / 3.0 / 3.1 EPR)
*   `PPS.md`: Programmable Power Supply (PD 3.0 子集)
*   `USBC-Current.md`: Type-C 1.5A / 3.0A (基於 CC Rp/Rd)
*   `BC12.md`: Battery Charging 1.2 (基於 D+/D- SDP/CDP/DCP)

### 跨聯盟標準
*   `UFCS.md`: 中國融合快充協議 (Universal Fast Charging Specification)

### 廠商專有協議 (Legacy & Proprietary)
*   `QC.md`: Qualcomm Quick Charge (2.0/3.0/4/4+/5)
*   `Apple.md`: Apple 2.4A (Divider Mode)
*   `FCP.md`: Huawei Fast Charge Protocol / Super Charge Protocol (SCP)
*   `AFC.md`: Samsung Adaptive Fast Charging
*   `VOOC.md`: OPPO VOOC / SuperVOOC
*   `PE.md`: MediaTek Pump Express (VBUS Pulsing)

## 維護原則
1.  **來源可靠性**: 本區內容應以 USB-IF、各協議官方組織或主要晶片廠商 (如 TI, NXP, Infineon) 發布的 Datasheet, App Note, Specification 為準。
2.  **不編造**: 若對於某些私有協議的底層細節 (如精確時序) 無法取得官方或交叉驗證的資料，請在文件中註明「資訊未公開」或「推測基於逆向工程」，不可自行編造。
3.  **可測試性**: 在編寫協議細節時，應思考「測試腳本如何驗證這段描述？」。盡量提供具體的電壓值、電阻值、頻率或握手步驟。
