# 🦞 PMU2CLAW Skills

> Fitipower IC Test Automation AI Skill Pack — TENJI · JD6628H · TIM2TENJI · Cadence AMS

[![Skills](https://img.shields.io/badge/skills-13-56d364?style=flat-square)](https://pmu2claw-dev.github.io/pmu2claw-skills/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-79c0ff?style=flat-square)](https://github.com/pmu2claw-dev/openclaw-skill)
[![Hermes](https://img.shields.io/badge/Hermes-compatible-79c0ff?style=flat-square)](https://github.com/pmu2claw-dev/hermes-agent-skill)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-d2a8ff?style=flat-square)](https://claude.ai/code)
[![License](https://img.shields.io/badge/license-MIT-8b949e?style=flat-square)](LICENSE)

這個 repo 收錄針對 Fitipower IC 測試自動化設計的 AI Skill，可用於 OpenClaw、Hermes、Claude Code 等 agent 平台。

🌐 **線上目錄：[https://pmu2claw-dev.github.io/pmu2claw-skills/](https://pmu2claw-dev.github.io/pmu2claw-skills/)**

功能包含：即時搜尋、Skill 詳細說明、References 瀏覽、修改歷程、相關 Skill 推薦。

---

## 📋 Skill 清單

### TENJI Core

| Skill | 說明 |
|---|---|
| [`tenji-guide`](tenji-guide/) | TENJI Excel 語法完整操作手冊（REV 0.2.11） |
| [`tenji-workflow`](tenji-workflow/) | TENJI 請求分類與 workflow 決策入口 |
| [`tenji-ready`](tenji-ready/) | 11 種充電協議的 workbook 模板與 Excel 映射 |
| [`protocol-knowledge`](protocol-knowledge/) | PD/PPS/QC/AFC 等充電協議知識庫 |

### JD6628H Analysis

| Skill | 說明 |
|---|---|
| [`jd6628h-single-power-mode-analysis`](jd6628h-single-power-mode-analysis/) | 單電源模式 SA test-plan 分析 |
| [`jd6628h-dual-power-mode-analysis`](jd6628h-dual-power-mode-analysis/) | 雙電源模式 SA 分析 |
| [`jd6628h-blind-insert-mode-analysis`](jd6628h-blind-insert-mode-analysis/) | 智能盲插模式 SA-plan 分析 |

### SA Plan → TENJI Pipeline

| Skill | 說明 |
|---|---|
| [`tenji-sa-plan-intake`](tenji-sa-plan-intake/) | 唯讀檢查 SA test plan Excel workbook |
| [`tenji-sa-plan-to-mother-template-mapping`](tenji-sa-plan-to-mother-template-mapping/) | SA plan 映射進 TENJI mother template |
| [`tenji-single-item-pipeline`](tenji-single-item-pipeline/) | 單項 TENJI 規格組裝與 roundtrip 驗證 |

### TIM2TENJI Development

| Skill | 說明 |
|---|---|
| [`tim2tenji-backend-feature-slice`](tim2tenji-backend-feature-slice/) | TIM2TENJI 後端 feature slice（TDD） |
| [`tim2tenji-project-detail-ui-slice`](tim2tenji-project-detail-ui-slice/) | TIM2TENJI 前端 UI slice |

### EDA / Simulation

| Skill | 說明 |
|---|---|
| [`cadence-ams-log-triage`](cadence-ams-log-triage/) | Cadence Xcelium/Spectre AMS log 分析 |

---

## ⚡ 快速安裝

### Hermes（推薦：tap 整包）

```bash
hermes skills tap add pmu2claw-dev/pmu2claw-skills
hermes skills install tenji-workflow
```

### Hermes（單一 skill）

```bash
hermes skills install https://raw.githubusercontent.com/pmu2claw-dev/pmu2claw-skills/main/tenji-workflow/SKILL.md
```

### Claude Code

```bash
# 直接讀取 SKILL.md 作為 context
cat tenji-workflow/SKILL.md | claude --print -
```

### OpenClaw

```bash
cp -r tenji-workflow ~/.openclaw/workspace/skills/
```

---

## 🔄 推薦 Skill Chain

```
protocol-knowledge → tenji-workflow → tenji-ready → tenji-guide
                                           ↑
jd6628h-*-analysis → tenji-sa-plan-intake → sa-plan-to-mother-template-mapping → tenji-single-item-pipeline
```

---

## 📁 Repo 結構

每個 skill 都是獨立目錄，結構如下：

```
<skill-name>/
├── SKILL.md          # Skill 主文件（描述、workflow、rules）
├── references/       # 詳細參考文件（可選）
│   ├── *.md
│   └── ...
└── scripts/          # 輔助腳本（可選）
    └── *.py
```

---

## 📄 License

MIT © [pmu2claw-dev](https://github.com/pmu2claw-dev)
