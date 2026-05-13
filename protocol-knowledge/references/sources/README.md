# Protocol Source Memory

目的：給 protocol agent 一個可持續讀寫的來源記憶，避免反覆搜尋同一批非官方來源。

## 使用規則
- 每次採集前，先讀最近的 `*-collection.md`、最近一份 `*-report.md` 與本 README。
- `*-report.md` 是給人看的收斂版；`*-collection.md` 是來源明細與採集記錄，兩者不要混寫。
- 對於 **非官方來源**：
  - 若過去已讀且已抽乾可用資訊，除非有明確新線索，否則不要重複搜尋/重讀。
  - 若只是不同網站轉貼同一份內容，視為重複來源，避免再投入。
- 對於 **官方來源**（spec body / vendor product page / datasheet / app note / EVK / reference design）：
  - 允許定期回查，目的是確認規格、版本、勘誤、產品頁更新。
  - 若回查，需註明是 `official-recheck`，並記錄是否有版本變更。
- 每次新增來源時，盡量記：domain、title、URL、type（official/cross-check/forum/distributor/media）、topic、status（new/seen/recheck/duplicate/skip）、why-it-matters。
- 若判定來源重複或低價值，也要記錄 `duplicate` / `skip` 與原因，避免下次再踩。

## 建議條目格式
- Date:
- Domain:
- Title:
- URL:
- Type:
- Topic:
- Status:
- Reason:
- Notes:

## 報告寫作規範（固定執行）
- 每次新的 protocol 報告都沿用既有 evening/morning report 風格：
  - 先寫 `採集概述`
  - 再寫 `具體更新內容`
  - 最後寫 `來源追蹤狀態`
- `*-report.md` **只寫這一輪新找到、或新確認、或新補強的資料**，不要把舊知識整份重述。
- 若只是回查舊官方來源，只有在以下情況才寫進 report：
  - 有版本差異
  - 補上過去缺的關鍵測試/架構資訊
  - 能改變 TenJI / protocol 的寫法或判斷
- 舊知識、完整背景、全量來源明細，留在 `official/`、`implementation/`、`benchmark/` 與 `*-collection.md`；不要塞爆 `*-report.md`。
- 若某輪主要是補強單一協議（例如 QC），report 應明講「這次新增了哪些 QC 資訊」，而不是再抄整份 QC 總論。

## 快速判斷
- official → 可重查
- distributor / forum / blog / media / repost → 優先去重，非必要不重查
