# Changelog

所有重要變更均記錄於此，格式依據 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)。

---

## [Unreleased]

---

## [1.4.0] — 2026-05-13

### Added
- **`tools/tenji_converter/`**：從 TIM2TENJI_skill 移入 5 支核心邏輯模組
  - `gates.py`、`normalizer.py`、`repair.py`、`memory_loader.py`、`memory_rules.py`
- **`protocol-knowledge/references/`**：協議大師知識庫完整快照（41 份文件）
  - `official/`：AFC、Apple、BC1.2、FCP、PD、PE、PPS、QC、UFCS、USB-C Current、VOOC（12 份協議規格整理）
  - `tenji-ready/`：20 份 Excel mapping 與 test-fields 對應表（可直接用於 TENJI 生成）
  - `implementation/`：DP/DM legacy 決策樹、事件鏈、物理介面說明
  - `benchmark/`：協議晶片對比表
  - `INDEX.md`、`README.md`、`STATUS-MATRIX.md`

---

## [1.3.0] — 2026-05-13

### Added
- **搜尋範圍擴展**（`index.html`）
  - Tools 卡片納入搜尋：工具名稱、docstring 描述、標籤均可搜尋；子群組與整個 Tools section 跟隨結果顯示/隱藏
  - CHANGELOG viewer 納入搜尋：命中時自動展開、橘色高亮匹配文字、section 邊框標示；清空搜尋則收合還原
  - 搜尋框 placeholder 與無結果提示更新，反映四個搜尋範圍（Skills、Tools、CHANGELOG）

---

## [1.2.0] — 2026-05-13

### Added
- **`tools/` 目錄**：新增 30 支連動工具腳本
  - `tools/scripts/`（15 支）：核心自動化腳本，含 `sheet_classifier.py`、`mode_expander.py`、`bootstrap_family.py`、`compile_tenji.py`、`generate_excel.py`、`spec_validator.py`、`spec_normalizer.py`、`ai_parser.py`、`template_reader.py`、`build_sa_index.py`、`auto_repair_spec.py`、`memory_loader.py`、`memory_rules.py`、`feedback_processor.py`、`verify_visual_integrity.py`
  - `tools/tenji_pipeline/`（8 支）：可 `pip install` 的 Python package，含 `convert_single_item`、`validate_single_item`、`assemble_workbook`、`verify_workbook` 四個 CLI 入口
  - `tools/examples/`（7 支）：JD6628H 單電源與盲插模式的產生腳本範例
- **`index.html` Tools 區塊**：動態載入三個子群組的工具卡片，含 docstring 描述、last updated 時間、原始碼查看 Panel、一鍵下載
- **README.md**：新增 `🔧 Tools` 章節，含目錄結構與 pip 安裝說明；新增 tools badge

---

## [1.1.0] — 2026-05-13

### Added
- **線上目錄頁面功能強化**（`index.html`）
  - 即時搜尋篩選：可依名稱、描述、標籤過濾 skill 卡片
  - Skill 詳細面板：點擊卡片從右側滑入，含 SKILL.md 完整內容與 References 瀏覽
  - 相關 Skills 推薦：面板底部自動顯示關聯 skill，支援直接跳轉
  - Last Updated 時間戳：每張卡片顯示最後更新日期（從 GitHub API 動態載入）
  - 動態 Skill 計數：header badge 自動計算，無需手動維護
  - README 展示區：可展開閱讀 README.md
  - 修改歷程區：從 GitHub Commits API 動態載入，支援「載入更多」
  - Flow Diagram 節點可點擊，直接開啟對應 skill 詳細內容
- **README.md**：新增完整 Skill 索引表、安裝指南、推薦 Skill Chain、Repo 結構說明，加入 GitHub Pages 網址

---

## [1.0.0] — 2026-05-13

### Added
- 初始發布 13 個 AI Skills：
  - **TENJI Core**：`tenji-guide`、`tenji-workflow`、`tenji-ready`、`protocol-knowledge`
  - **JD6628H Analysis**：`jd6628h-single-power-mode-analysis`、`jd6628h-dual-power-mode-analysis`、`jd6628h-blind-insert-mode-analysis`
  - **SA Plan → TENJI Pipeline**：`tenji-sa-plan-intake`、`tenji-sa-plan-to-mother-template-mapping`、`tenji-single-item-pipeline`
  - **TIM2TENJI Development**：`tim2tenji-backend-feature-slice`、`tim2tenji-project-detail-ui-slice`
  - **EDA / Simulation**：`cadence-ams-log-triage`
- `index.html` 線上目錄頁（深色主題，Quick Install banner，Skill 卡片，推薦 Skill Chain 流程圖）

---

[Unreleased]: https://github.com/pmu2claw-dev/pmu2claw-skills/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/pmu2claw-dev/pmu2claw-skills/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/pmu2claw-dev/pmu2claw-skills/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/pmu2claw-dev/pmu2claw-skills/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/pmu2claw-dev/pmu2claw-skills/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/pmu2claw-dev/pmu2claw-skills/releases/tag/v1.0.0
