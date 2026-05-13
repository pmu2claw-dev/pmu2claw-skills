# Tenji2uvm 完整流程

## 一、PC 端處理

### Step 1: 取得轉檔工具
```
Copy Y:/CAD/Public/Bin/TenjiC_rev0.1.7z 到自己的 PC
解壓縮 → 找到 TenjiC_rev0.1.exe
```

### Step 2: 準備 Tenji Excel
```
Copy Y:\CAD\Public\Bin\Tenji_DOC\專案名稱_內碼名稱_外碼名稱_TenjiV2.1_R0.1.xlsm
```

### Step 3: 語法檢查
執行 `Tenji_QA` 檢查語法

### Step 4: 轉檔
1. 執行 `TenjiC_rev0.1.exe`
2. 選擇要轉檔的 Tenji Excel
3. 執行 `Tenji2uvm`
4. 正常完成 → 產生新目錄，內含 **39 個檔案**

**注意事項：**
- 路徑名稱不能有特殊字元：`(`, `)`, 中文字
- 不正常結束 → 聯絡 smith (CAD3, ext: 8009)

---

## 二、Workstation 端處理

### Step 1: 複製模板

**有 I2C 或 SWD 的專案：**
```bash
cp /home1/gmo/user/smith/SIM/TENJI/TENJI_TEMPLATE.tar.gz .
```

**沒有 I2C 也沒有 SWD 的專案：**
```bash
cp /home1/gmo/user/smith/SIM/TENJI/TENJI_TEMPLATE_NO_I2C.tar.gz .
```

### Step 2: 解壓縮 & 改名
```bash
gtar zxvf TENJI_TEMPLATE.tar.gz
mv TENJI_TEMPLATE TENJI_EK88512    # 改成你的 project name，必須 TENJI_ 開頭
```

### Step 3: 上傳檔案
把 PC 端 Tenji2uvm 產出的目錄內容上傳到：
```
TENJI_EK88512/Tenji_files/
```

### Step 4: 修改 cds.lib
掛上 DUT 相關的 library。

### Step 5: 開啟 icfb
```bash
cd TENJI_EK88512
qview_icfb
```

### Step 6: 建立環境（Library Manager）

1. 建立 `TENJI_EK88512` 目錄
2. Import verilog → 建立 `test_uvm` 和 `CP_MODULES` 兩個 cell
3. 建立 test bench → cell name 必須是 `uvm_tb_ek88512`（**必須全小寫**）

### Step 7: Test Bench 設定

Test bench 包含 3 個 sub-cell：
| Sub-cell | Instance Name |
|----------|---------------|
| test_uvm | `test` |
| CP_MODULES | `CPM` |
| DUT | `DUT` |

→ 長出所有 net → Check and Save

### Step 8: Config View（HED）

1. 建立 `uvm_tb_ek88512` 的 config view
2. Cell == `test_uvm` → 設成 **External HDL**
3. DUT 相關的 APR 及 MTP → 設成 **symbol**
4. Save config view

### Step 9: Maestro 設定

1. 建立 maestro view
2. Simulator 選擇 **spectreX**
3. 設定 connect rules
4. Simulation → Options → AMS Simulator → Include options → `./tb/uvmArgs_wi_i2c`

### Step 10: GUI Mode 執行

Run → 確認結果正確 → 產生 netlist
- 成功：在 `~user_home/simulation/` 下產生正確 netlist
- 失敗原因：
  - Tenji file 有問題（RD check）
  - Tenji2uvm 程式問題（聯絡 smith）

### Step 11: BATCH Mode 執行

有了正確 netlist 後：
1. icfb 可關可開
2. 建立 BATCH 環境
3. 執行 BATCH mode simulation

### Step 12: 查看結果

- BATCH mode 完成後產生 summary reports
- Reports 格式包含各測項的 Pass/Fail 狀態
- 可整理出 simulation time 及 total test time

---

## Tenji Flow 優點

- RD 與 TE 使用同一份 Tenji Excel，減少溝通落差
- 自動化產生 UVM simulation code
- 標準化測試流程
- 減少人工轉換的 typo

---

## 聯絡資訊

- **TenjiApp_rev0.1 維護：** CAD3 smith.hsu, ext: 8009
- **Email:** Smith.hsu@fitipower.com
