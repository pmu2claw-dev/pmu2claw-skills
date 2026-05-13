# Q&A 與重要規則

## 常見問題

### Q1: 為何要用 Pseudo Code？

如果 I2C command list 很多，一行一行寫到 H 欄位會造成可讀性差、難以 debug。
用 Pseudo Code 把常用 command list 包裝成巨集指令，可以提升可讀性、減少 typo、方便 debug。

### Q2: 為何不能轉 Tenji Excel？

請檢查：
1. 是否 copy 自正確路徑：`Y:\CAD\Public\Bin\Tenji_DOC\專案名稱_TenjiV2.1_R0.1.xlsm`
2. 是否先執行 `Tenji_QA` 語法檢查
3. 是否用 `TenjiC_rev0.1` 選擇 `Tenji2uvm` 做轉換
4. **路徑名稱不能有特殊字元**（`(`, `)`, 中文字等）— 會造成錯誤結果

---

## 重要規則彙整

### 命名規則
- 量測時間的測項名稱 → 必須用 `_TMU` 結尾
- `PWR_OS` → 只能用於 Open Short test，不能用於其他測項
- `IQ_` 或 `Leak_` 開頭的 ForceV → 電壓不能小於 PinMap N/O 欄所列電壓（轉 Tenji2uvm 時會 error）

### PseudoCode 規則
- MTP 跟 GBY 的 I2C code → 支援「部分 bits」定義
- Pseudo Code sheet 中的巨集可增加可讀性

### Trim 規則
- `TuneI` 可在結尾加 Vclamp
- `TuneV` 可在結尾加 Iclamp

### Pattern 規則
- Pattern file 支援 `SET_LEVEL` 指令
- Pattern 可用 `LOOP` 方式生成重複 pattern

### FuseTrim vs CHECK_ACK
- `FuseTrim` → **LSB first**
- `CHECK_ACK` → **MSB first**

### CHECK_MTP 補充
- 有使用補充說明，請注意搭配使用方式

### F 欄規則
- F 欄支援註解功能（`//` 開頭）

---

## 更新日誌摘要（REV 0.2.11）

| 日期 | 更新內容 |
|------|---------|
| 2024/05/24 | UR 可用於 G 欄 & H 欄 |
| 2024/05/30 | Pattern 新增 SET_LEVEL |
| 2024/06/04 | 新增 FuseTrim |
| 2024/06/17 | F 欄註解功能 |
| 2024/06/27 | 新增 CHECK_ACK |
| 2024/08/19 | 新增 Wait_MTP；_TMU 命名規則 |
| 2024/12/02 | PWR_OS 僅限 Open Short test |
| 2024/12/12 | MTP/GBY I2C 部分 bits；LoadRegulation/LineRegulation |
| 2024/12/30 | TuneI+Vclamp / TuneV+Iclamp / CHECK_MTP 補充 |
| 2025/01/22 | IQ_/Leak_ 開頭 ForceV 電壓自動檢查 |
| 2025/02/05 | 新增 LoadReg_dc2dc |
| 2025/03/25 | PseudoCode 用法解說 |
| 2025/09/26 | P/Q/R/S 欄位 & Leakage 1.1 倍解說 |
| 2025/10/15 | Pattern LOOP 生成 |
| 2026/03/13 | 更新上架流程 |
