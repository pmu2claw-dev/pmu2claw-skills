# USB Type-C Current (Type-C Rp/Rd)

## 1. 簡介與運作原理
USB Type-C 規範定義了一套不依賴數據線（D+/D-）也不依賴 USB PD 數位通訊的基礎供電廣播機制。這套機制完全基於 CC (Configuration Channel) 腳位上的電阻網路（Pull-up Resistor, Rp 與 Pull-down Resistor, Rd）來完成設備的插入偵測（Attach/Detach）、主從角色辨識（Source/Sink）以及 **供電電流能力（Current Capability）的廣播**。

這被稱為 **USB Type-C Current**。這是在沒有建立 USB PD 通訊前，Type-C 介面**最基礎且保底的供電標準**。電壓固定為 **5V**（依標準容許範圍通常為 4.75V ~ 5.5V）。

## 2. 角色與電阻定義

### Source 端 (供電端, DFP)
Source 端必須在 CC1 與 CC2 腳位上各配置一個上拉電阻（**Rp**），將電壓拉至 VBUS、3.3V 或 5V 內部參考電源。**Rp 的阻值（或等效的電流源大小）決定了 Source 宣告的供電能力。**

根據 Type-C 規範，Source 可宣告三種電流能力：
1.  **Default USB Power** (USB 2.0 為 500mA，USB 3.x 為 900mA)
2.  **USB Type-C Current @ 1.5A** (最大 7.5W)
3.  **USB Type-C Current @ 3.0A** (最大 15W)

| Source 宣告能力 | 需搭配之 Rp 阻值 (上拉至 5V) | 需搭配之 Rp 阻值 (上拉至 3.3V) | 等效電流源 (Current Source) |
| :--- | :--- | :--- | :--- |
| **Default USB** | 56 kΩ ± 20% | 36 kΩ ± 20% | 80 µA ± 20% |
| **1.5 A @ 5V** | 22 kΩ ± 5% | 12 kΩ ± 5% | 180 µA ± 8% |
| **3.0 A @ 5V** | 10 kΩ ± 5% | 4.7 kΩ ± 5% | 330 µA ± 8% |

### Sink 端 (受電端, UFP)
Sink 端必須在 CC1 與 CC2 腳位上各配置一個下拉電阻（**Rd**），阻值固定為 **5.1 kΩ ± 10%**，接地。

## 3. 電流能力偵測流程 (Sink 視角)

當 Sink 設備（例如手機）插入 Source 端（例如充電器）時：
1.  **Attach Detect**: Sink 的 Rd (5.1kΩ) 會與 Source 的 Rp 形成分壓網路。Sink 的 Type-C Controller 會監測 CC 腳位的電壓（vRd）。
2.  **Capability Decode**: 根據讀取到的 vRd 電壓落在哪個區間，Sink 判斷 Source 能提供多少電流，並嚴格限制自身的抽載（Draw）不超過該上限，以防 Source 過載重啟。

**vRd 電壓閾值判定 (以 Sink 端內部 ADC 讀取值為準):**

*   **vRd < 0.20V**: 未連接 (vRA 狀態，通常是接到了 e-Marker 線纜但未接供電端) 或異常。
*   **0.25V < vRd < 0.66V**: 識別為 **Default USB Power**。Sink 應將電流限制在 500mA/900mA，或依賴 D+/D- 進行 BC1.2 / 私有協議協商來獲取更大電流。
*   **0.66V < vRd < 1.23V**: 識別為 **USB Type-C Current 1.5A**。Sink 可安全抽載至 1.5A。
*   **1.23V < vRd < 2.04V**: 識別為 **USB Type-C Current 3.0A**。Sink 可安全抽載至 3.0A。

## 4. 多協議共存下的優先級
USB Type-C Current (Rp/Rd) 的優先級定義極為重要，尤其是與 BC1.2 及 USB PD 共存時：
1.  **USB PD > Type-C Current**: 若雙方成功建立 USB PD 通訊，則以 PD 協商出的 PDO (電壓/電流) 為準，**完全忽略 CC 腳位上 Rp 廣播的 1.5A/3.0A 限制**。這也是為何高瓦數充電器（例如 65W, 20V/3.25A）其 Rp 可能只設為 Default USB 或 1.5A，真實大功率由 PD 數位訊號解鎖。
2.  **Type-C Current > BC 1.2**: 根據 Type-C 標準，若設備不支援 PD 或 PD 失敗，且 CC 腳偵測到 1.5A 或 3.0A 的 Rp 廣播，Sink 允許直接抽取 1.5A 或 3.0A 的電流，**無需再經過 D+/D- 的 BC1.2 SDP/CDP/DCP 偵測**。只有當 Rp 廣播為 "Default USB" 時，Sink 才必須回退到 BC1.2 流程去判斷是否能抽 1.5A。
3.  **動態變化**: Source 允許在供電過程中動態改變 Rp 的阻值（例如系統供電吃緊時從 3.0A 降為 1.5A）。Sink 必須具備即時監控 vRd 並在 tSinkAdj (通常幾十毫秒) 內降低負載電流的能力，否則可能導致 Source 過流保護。
