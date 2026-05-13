# Protocol Knowledge Index

最後更新：2026-04-21

## 1. 知識庫定位

這份 index 是協議大師知識庫的總入口，目的是回答三件事：

1. 目前收了哪些協議
2. 每類知識放在哪
3. 哪些內容已可直接給 TenJI / 腳本 / Excel 使用，哪些還要補

---

## 2. 先看哪裡

- 結構總覽：`README.md`
- 覆蓋總表：`STATUS-MATRIX.md`
- 官方與標準入口：`official/index.md`
- 來源追蹤規則：`sources/README.md`
- TenJI-ready 入口：`tenji-ready/`

---

## 3. 協議覆蓋狀態

### 已有官方/標準整理
- PD → `official/PD.md`
- PPS → `official/PPS.md`
- BC1.2 → `official/BC12.md`
- UFCS → `official/UFCS.md`
- QC → `official/QC.md`
- Apple 2.4A → `official/Apple.md`
- FCP / SCP → `official/FCP.md`
- AFC → `official/AFC.md`
- VOOC / SuperVOOC → `official/VOOC.md`
- PE → `official/PE.md`
- USB-C Current → `official/USBC-Current.md`

### 已有實作/硬體面整理
- 實體介面 / 訊號路徑 → `implementation/physical-interface.md`
- Legacy D+ / D- 協議分流樹 → `implementation/legacy-dpdm-decision-tree.md`
- Legacy D+ / D- 事件鏈 → `implementation/legacy-dpdm-event-chain.md`
- 協議晶片比較 → `benchmark/protocol-chips.md`

### 已轉成 TenJI-ready
- PD → `tenji-ready/PD-test-fields.md`, `tenji-ready/PD-excel-mapping.md`
- PPS → `tenji-ready/PPS-test-fields.md`, `tenji-ready/PPS-excel-mapping.md`
- BC12 → `tenji-ready/BC12-test-fields.md`, `tenji-ready/BC12-excel-mapping.md`
- Type-C Current → `tenji-ready/TypeC-Current-test-fields.md`, `tenji-ready/TypeC-Current-excel-mapping.md`
- UFCS → `tenji-ready/UFCS-test-fields.md`, `tenji-ready/UFCS-excel-mapping.md`
- QC → `tenji-ready/QC-excel-mapping.md`
- PE → `tenji-ready/PE-test-fields.md`, `tenji-ready/PE-excel-mapping.md`
- FCP / SCP → `tenji-ready/FCP-test-fields.md`, `tenji-ready/FCP-excel-mapping.md`
- AFC → `tenji-ready/AFC-test-fields.md`, `tenji-ready/AFC-excel-mapping.md`
- VOOC / SuperVOOC → `tenji-ready/VOOC-test-fields.md`, `tenji-ready/VOOC-excel-mapping.md`

---

## 4. 來源與報告區

### 用途分工
- `sources/*-collection.md`：每輪找過哪些來源、為什麼留/跳過
- `sources/*-report.md`：給人看的本輪新增 / 新確認 / 新補強
- `sources/README.md`：來源追蹤規範

### 現況
- 已累積多輪 2026-04-13 ~ 2026-04-17 的 collection / report 記錄
- 可回看哪些官方來源已查過，避免重複搜尋
- 目前 protocol 自動 cron 已停用，所以後續新增知識以手動整理為主

---

## 5. 建議使用方式

### 如果要查協議本體
先看：
1. `official/index.md`
2. 對應協議的 `official/*.md`
3. 有需要再看 `sources/*-report.md` 補最近更新

### 如果要做腳本 / Excel / TenJI 測項
先看：
1. `STATUS-MATRIX.md`
2. `tenji-ready/*-test-fields.md`
3. `tenji-ready/*-excel-mapping.md`
4. 必要時回查 `official/*.md`

### 如果要確認來源可靠度
先看：
1. `sources/README.md`
2. 最近一輪 `*-collection.md`
3. 最近一輪 `*-report.md`

---

## 6. 目前缺口 / 待整理

### 結構面
- 補 protocol 知識庫維護流程（新增協議時要更新哪些地方）
- 補 benchmark / implementation 的更細入口檔
- 持續整理 archive 封存區，避免正式區混入過期版本

### 內容面
- Apple 2.4A 已補成 TenJI-ready：`tenji-ready/Apple-test-fields.md`、`tenji-ready/Apple-excel-mapping.md`
- PD / PPS / UFCS 還可再補 script skeleton
- benchmark 區可補 controller / charger IC / protection IC 對應矩陣
- 可把 `implementation/legacy-dpdm-decision-tree.md` 再拆成圖像版
- 可把 `implementation/legacy-dpdm-event-chain.md` 再拆成 TenJI decision table / state-machine schema

---

## 7. 一句話總結

現在協議大師知識庫已經不只是資料堆，而是有：
- 官方知識區
- 實作區
- 來源追蹤區
- TenJI-ready 區
- 覆蓋總表 `STATUS-MATRIX.md`

接下來主要工作不是重建，而是**補缺口、維護品質、繼續擴充**。
