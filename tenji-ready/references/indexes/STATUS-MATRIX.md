# Protocol Coverage Matrix

最後更新：2026-04-21

| Protocol | Official | Implementation / HW | Benchmark | TenJI Test Fields | TenJI Excel Mapping | Status | Notes |
|---|---|---|---|---|---|---|---|
| PD | ✅ `official/PD.md` | ◐ `implementation/physical-interface.md` | ◐ `benchmark/protocol-chips.md` | ✅ `tenji-ready/PD-test-fields.md` | ✅ `tenji-ready/PD-excel-mapping.md` | ready | 主幹完整，可再補 EPR / AVS 細項 |
| PPS | ✅ `official/PPS.md` | ◐ | ◐ | ✅ `tenji-ready/PPS-test-fields.md` | ✅ `tenji-ready/PPS-excel-mapping.md` | ready | 可再補 keep-alive / APDO 掃描細項 |
| BC1.2 | ✅ `official/BC12.md` | ◐ | ◐ | ✅ `tenji-ready/BC12-test-fields.md` | ✅ `tenji-ready/BC12-excel-mapping.md` | ready | D+/D- threshold 可再補量測細節 |
| USB-C Current | ✅ `official/USBC-Current.md` | ◐ | ◐ | ✅ `tenji-ready/TypeC-Current-test-fields.md` | ✅ `tenji-ready/TypeC-Current-excel-mapping.md` | ready | 可再補 Rp/Rd 實測矩陣 |
| UFCS | ✅ `official/UFCS.md` | ◐ | ◐ | ✅ `tenji-ready/UFCS-test-fields.md` | ✅ `tenji-ready/UFCS-excel-mapping.md` | ready | 後續可補正式 script skeleton |
| QC | ✅ `official/QC.md` | ◐ | ◐ | — | ✅ `tenji-ready/QC-excel-mapping.md` | partial | 缺公開完整 timing；以 partial / cross-checked 為主 |
| PE | ✅ `official/PE.md` | ◐ | ◐ | ✅ `tenji-ready/PE-test-fields.md` | ✅ `tenji-ready/PE-excel-mapping.md` | ready | VBUS pulsing 需示波器/電流探棒驗證 |
| FCP / SCP | ✅ `official/FCP.md` | ◐ | ◐ | ✅ `tenji-ready/FCP-test-fields.md` | ✅ `tenji-ready/FCP-excel-mapping.md` | ready | FCP 與 SCP 建議分開測項群 |
| AFC | ✅ `official/AFC.md` | ◐ | ◐ | ✅ `tenji-ready/AFC-test-fields.md` | ✅ `tenji-ready/AFC-excel-mapping.md` | ready | 與 QC 2.0 相似但不可混寫 |
| VOOC / SuperVOOC | ✅ `official/VOOC.md` | ◐ | ◐ | ✅ `tenji-ready/VOOC-test-fields.md` | ✅ `tenji-ready/VOOC-excel-mapping.md` | ready | 因封閉性高，測項應標示 partial / not-public 邊界 |
| Apple 2.4A | ✅ `official/Apple.md` | ◐ | ◐ | ✅ `tenji-ready/Apple-test-fields.md` | ✅ `tenji-ready/Apple-excel-mapping.md` | ready | divider mode / current unlock 已補齊 |

## 判讀規則
- `ready`：至少已有 official + TenJI-ready 入口，可支援後續腳本/Excel整理
- `partial`：已有部分 TenJI-ready，但公開規格不足，必須保留不確定標記
- `todo`：尚未整理成 TenJI-ready
- `◐`：已有相關共用文件，但不是每個協議都拆成獨立專章

## 建議下一輪優先順序
1. PD / PPS / UFCS 補 script skeleton
2. benchmark 區補 controller / charger IC / protection IC 對應矩陣
3. implementation 區補 D+/D- mux / analog front-end / path isolation 圖解
4. 把 `legacy-dpdm-decision-tree.md` / `legacy-dpdm-event-chain.md` 再延伸成圖像版 / TenJI decision table / state-machine schema
