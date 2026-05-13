# Protocol Knowledge Base

這個資料夾是「協議大師 / Protocol Librarian」的共享知識庫，目的是把**快充協議的官方規格、可追溯來源、實體實作、晶片比較、以及 TenJI 可直接落地的測試結構**整理在同一個地方。

## 先看哪裡

- `INDEX.md`：整體知識地圖、覆蓋範圍、目前狀態、待補區塊
- `official/`：各協議的官方 / 可交叉驗證規格說明（Golden Reference）
- `implementation/`：實體信號路徑、介面與硬體實作
- `benchmark/`：協議相關晶片與控制器比較
- `tenji-ready/`：已轉成 TenJI / Excel / script 可用格式的內容
- `sources/`：每輪蒐集、回查、報告與來源追蹤記錄

## 目錄結構

- `official/`
  - `index.md`：官方與標準知識入口
  - `PD.md` / `PPS.md` / `BC12.md` / `UFCS.md` / `QC.md` / `Apple.md` / `FCP.md` / `AFC.md` / `VOOC.md` / `PE.md` / `USBC-Current.md`
- `implementation/`
  - `physical-interface.md`
  - `legacy-dpdm-decision-tree.md`：Apple / BC1.2 / QC / AFC / FCP / UFCS 在 D+ / D- 路徑上的分流與共存邏輯
  - `legacy-dpdm-event-chain.md`：把 baseline / analog / digital / fallback 拆成事件鏈，適合往 state-machine / TenJI 流程落地
- `benchmark/`
  - `protocol-chips.md`
- `tenji-ready/`
  - `*-test-fields.md`：測項欄位骨架
  - `*-excel-mapping.md`：TenJI / Excel 對應欄位整理
- `sources/`
  - `README.md`：來源記錄規則
  - `*-collection.md`：來源蒐集明細
  - `*-report.md`：給人看的收斂報告

## 目前狀態（2026-04-21）

- 協議主體知識已經落地在 `official/`、`implementation/`、`benchmark/`
- TenJI-ready 已涵蓋 `PD / PPS / BC12 / TypeC Current / UFCS / QC / PE / FCP / AFC / VOOC / Apple 2.4A`
- `sources/` 已累積多輪採集與報告記錄，可作為回查依據
- 先前 protocol 自動 report / collect cron 已停用；目前這份知識庫以**手動整理與人工續修**為主
- `implementation/legacy-dpdm-decision-tree.md` 已整理 legacy D+ / D- 世界的 baseline / analog / digital 三層分流
- `implementation/legacy-dpdm-event-chain.md` 已把上述分流往下拆成可執行的事件鏈
- 目錄中仍有少量暫存 / patch / orig 檔，後續可再做一次清理
