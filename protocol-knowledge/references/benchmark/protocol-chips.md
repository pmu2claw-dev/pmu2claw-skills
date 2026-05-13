# 快充協議晶片市場參考 (Protocol Chips Benchmark)

此文檔收集市場上常見的 Type-C 控制器、PD 控制器與快充 IC，以了解各廠牌實作協議的方式。此資料表可協助測試時選擇標的，並了解市面上控制器的功能分界。

## 控制器分類 (Category)

1.  **Protocol Controller / PHY (TCPC)**: 僅負責實體層 (CC/BMC 或 D+/D-) 通訊與基礎信號轉換，需搭配外部 MCU / AP / EC 處理協議邏輯。(如：TCPC 規範的晶片)
2.  **PD Controller**: 內建狀態機或微控制器，自主處理 PD 協商與部分其他協議，可能內建高壓 LDO 與部分保護電路，輸出控制信號給外部電源轉換器或負載開關。(如：Infineon PMG1, Realtek RTS54xx)
3.  **Type-C Port Controller**: 支援 Type-C 插拔偵測與簡單電流配置，未必支援完整 PD 訊息。
4.  **Charger IC (Power Path Integration)**: 結合協議控制器與 Buck-Boost 功率轉換器，提供單晶片快充解決方案，通常用於 Sink 端 (手機/筆電) 充放電管理或 Source 端 (車充/移動電源)。(如：Southchip SC20xx)
5.  **Front-End Protection IC (OVP/OCP)**: 位於 Type-C 接口第一線，保護後端控制器免受高壓 (如 VBUS 短路到 CC) 損害，不處理複雜協議，但可能輔助實體層防護。
6.  **MCU-assisted solution**: 具有軟體可編程空間 (Flash/RAM) 的通用 MCU，搭配 Type-C 類比前端 (AFE) 達成協議支援。

## 晶片總覽

| Vendor | Part Number | Category | Supported Protocols | Max Power / V / I | Port Type | Host Interface | Analog/PHY | Power Path Integration | Target Product | Public Docs | Evidence Level | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Infineon** | EZ-PD PMG1-S3 | PD Controller / MCU | PD 3.1 EPR, PPS, QC 4.0, Apple, BC1.2 | 140W+ (28V EPR) | DRP | I2C, SPI, UART | CC PHY, D+/D- ADC | None (Controls ext FET) | MCU/IoT, Sink/Source | Yes | verified-official | 內建 ARM Cortex-M0+ |
| **onsemi** | FUSB302B | TCPC / PHY | PD 3.0, Type-C 1.2 | 100W | DRP | I2C | CC PHY (BMC Tx/Rx) | None | Smartphones, IoT | Yes | verified-official | 極簡 TCPC，需 MCU 跑協定棧 |
| **NXP** | PTN5110 | TCPC | PD 3.0, Type-C 1.2 | 100W | DRP | I2C | CC PHY (TCPCI) | None | PC, Notebooks | Yes | verified-official | 標準 TCPCI 介面，支援 Fast Role Swap (FRS) |
| **ST** | STUSB4500 | PD Controller | PD 3.0 (Sink Only) | 100W (20V/5A) | Sink | I2C | CC PHY, VBUS Switch Gate | None (Gate driver) | IoT, Sink devices | Yes | verified-official | 內建 NVM，硬體自主協商不需 MCU |
| **Renesas** | RAA489204 | Charger IC | PD 3.0, PPS, BC1.2 | 100W (20V/5A) | DRP / Sink | I2C, SMBus | CC PHY, D+/D- | Bi-dir Buck-Boost | Notebooks, Power Banks | Yes | cross-checked | 高度整合充電與 PD 協議 |
| **Realtek** | RTS5452E | PD Controller | PD 3.0, PPS | 100W | DRP | I2C, SMBus | CC PHY | None (Gate driver) | PC, Hub, Dock | NDA | cross-checked | 支援 Type-C Port 控制與 PD |
| **VIA Labs** | VL103 / VL105 | PD Controller | PD 3.0 | 100W | DRP | I2C | CC PHY | None | PC, Hub, Dongle | NDA | cross-checked | 專注於 Hub/Dongle 的 PD 應用 |
| **Southchip** | SC2021A | Charger IC / PD | PD 3.0, PPS, QC, FCP, AFC | 100W | DRP | I2C | CC, D+/D- | Buck-Boost Controller | Power Banks, Car Chg | NDA | partial | 單晶片高整合 (Protocol + Buck-Boost) |
| **TI** | TPS65987D | PD Controller | PD 3.0, Thunderbolt 3 | 100W (20V/5A) | DRP | I2C, SPI | CC PHY | Internal Power Switch | PC, Notebooks, Hubs | Yes | verified-official | 高階 PD 控制器，內建 20V/5A 開關 |
| **Richtek** | RT1715 | Protocol Controller | PD 3.0, Type-C 1.2 | 100W | DRP | I2C (TCPCI) | CC PHY | None | Smartphones, PC | Yes | cross-checked | 依賴外部 TCPM (Host) 處理協議 |

## Notes on Implementation
- **Multiprotocol conflict resolution**: Many controllers that support PD and legacy protocols (QC/FCP) will prioritize PD. If PD negotiation fails, they fall back to polling D+/D- for legacy protocols.
- **Analog/PHY details**: TCPCs generally only include the BMC CC transceiver and Rd/Rp resistors. Chips supporting QC/AFC/UFCS must also include D+/D- multiplexers, ADCs, and UARTs.
| **TI** | TPS25810 | Type-C Port Controller | Type-C 1.2 (3A/1.5A) | 15W (5V/3A) | Source | I2C / HW pins | CC PHY, VBUS Switch | Internal VBUS FET | USB Wall Chargers, Hubs | Yes | verified-official | Basic DFP (Source) controller, no PD BMC, uses CC Rp resistors to advertise 1.5A/3.0A. |
