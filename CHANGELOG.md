# Changelog

所有重要變更均記錄於此，格式依據 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)。

---

## [Unreleased]

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

[Unreleased]: https://github.com/pmu2claw-dev/pmu2claw-skills/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/pmu2claw-dev/pmu2claw-skills/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/pmu2claw-dev/pmu2claw-skills/releases/tag/v1.0.0
