# SAD System - Product Requirements Document (PRD)
# 產品需求文件

> **Version**: 1.0.0  
> **Last Updated**: 2026-01-14  
> **Author**: Yusei

---

## 1. Executive Summary | 執行摘要

### 1.1 Vision | 願景

**EN**: SAD System (SLASH@DASH) is a universal LLM command interface that bridges natural language and programmatic instructions through "strict syntax, lenient vocabulary" design philosophy.

**中文**: SAD System (SLASH@DASH) 是一個萬用 LLM 指令介面，透過「用法嚴格，用字寬容」的設計理念，橋接自然語言與程式化指令。

### 1.2 Core Value Proposition | 核心價值主張

| Value | 價值 | Description | 說明 |
|-------|------|-------------|------|
| Safety | 安全性 | S.A.B.E. protocol ensures zero-error automation | S.A.B.E. 協議確保零錯誤自動化 |
| Flexibility | 彈性 | Synonym mapping accepts diverse vocabulary | 同義詞映射接受多樣化用語 |
| Predictability | 可預測性 | Fixed syntax ensures consistent parsing | 固定語法確保一致解析 |

---

## 2. Target Users | 目標用戶

| Persona | 用戶類型 | Use Case | 使用場景 |
|---------|---------|----------|----------|
| AI Power Users | AI 進階用戶 | Frequent LLM interaction | 頻繁 LLM 互動 |
| Developers | 開發者 | Building AI-powered tools | 建構 AI 驅動工具 |
| Prompt Engineers | Prompt 工程師 | Standardized prompt workflows | 標準化 prompt 工作流程 |

---

## 3. Core Features | 核心功能

### 3.1 Command Parser | 指令解析器

**Syntax | 語法**: `/verb-noun @input:id --param value`

```bash
# Example | 範例
/analyze-data @file:sales.csv --format markdown --type summary
```

| Component | 組成部分 | Format | 格式 | Required | 必填 |
|-----------|---------|--------|------|----------|------|
| Command | 指令名 | `/verb-noun` | `/動詞-名詞` | ✅ | ✅ |
| Input | 輸入 | `@type:id` | `@類型:識別符` | Optional | 可選 |
| Parameters | 參數 | `--key value` | `--鍵 值` | Optional | 可選 |

### 3.2 Verb Mapping | 動詞映射

**Principle | 原則**: Strict syntax, lenient vocabulary | 用法嚴格，用字寬容

| Standard Command | 標準指令 | Accepted Synonyms | 接受的同義詞 | Weight | 權重 |
|------------------|---------|-------------------|-------------|--------|------|
| `/analyze-data` | 分析數據 | analyze, inspect, examine, investigate | 95-100 |
| `/summarize-doc` | 摘要文件 | summarize, digest, condense, brief | 90-100 |
| `/convert-file` | 轉換檔案 | convert, transform, change | 88-100 |
| `/delete-file` | 刪除檔案 | delete, remove, erase ⚠️ | 90-100 |

**Thresholds | 閾值**:
- Direct mapping | 直接映射: ≥ 90%
- S.A.B.E. trigger | S.A.B.E. 觸發: < 90%
- Reject | 拒絕: < 30%

### 3.3 S.A.B.E. Protocol | S.A.B.E. 協議

**Definition | 定義**: **S**uggest & **A**sk **B**efore **E**xec

| Mode | 模式 | Trigger | 觸發條件 | Example | 範例 |
|------|------|---------|---------|---------|------|
| A: Ambiguous Repair | 模糊修復 | Low confidence mapping | `/figure-out @data` |
| B: Error Recovery | 錯誤恢復 | Invalid input | `@file:nonexistent.csv` |
| C: Large Task Confirm | 大型任務確認 | Token > 50k or Steps > 5 | `/full-workflow --complete` |
| D: High Risk Confirm | 高風險確認 | Destructive operations | `/deploy-site`, `/delete-file` |
| E: Input Missing | 輸入缺失 | Required input not provided | `/analyze-data` (no @input) |

### 3.4 Five Prompt Hacks | 五言絕句 ⭐ NEW

**Concept | 概念**: Auto-inject quality-enhancing prompts at progress milestones | 在進度里程碑自動注入品質提升附言

| Progress | 進度 | Hack Name | 名稱 | Postscript Effect | 附言效果 |
|----------|------|-----------|------|-------------------|---------|
| 20% | 🎯 Clarify | 先澄清 | Ask clarifying questions first | 先問澄清問題 |
| 40% | 🌐 Web-backed | 網路查證 | Search web for recent info | 搜尋最新資訊 |
| 60% | 📊 Self-grade | 自我評分 | Iterate until 9/10 quality | 迭代至 9/10 品質 |
| 80% | 👥 3-Expert Panel | 三專家 | Multi-perspective analysis | 多角度分析 |
| ~100% | 😈 Devil's Advocate | 自我批判 | Self-critique for blind spots | 找出盲點 |

**UI: Progress Indicator | 進度指示器**
```
🎯  🌐  📊  👥  😈
●   ●   ○   ○   ○   ← Current progress | 當前進度
20% 40% 60% 80% 100%
```

### 3.5 Undo System | 恢復上一動 ⭐ NEW

| Command | 指令 | Function | 功能 |
|---------|------|----------|------|
| `/undo` | 恢復上一動 | Restore previous state | 恢復上一狀態 |
| `/undo --steps 3` | 恢復前三步 | Restore N steps back | 恢復 N 步 |
| `/undo --preview` | 預覽恢復 | Preview what will be restored | 預覽將恢復內容 |
| `/redo` | 重做 | Redo undone action | 重做被撤銷操作 |
| `/history` | 歷史清單 | Show reversible history | 顯示可恢復歷史 |

---

## 4. Complete Command Reference | 完整指令參考

### 4.1 Data Commands | 數據指令

| Command | 指令 | Description | 說明 | Risk | 風險 |
|---------|------|-------------|------|------|------|
| `/analyze-data` | 分析數據 | Perform data analysis | 執行數據分析 | Low | 低 |
| `/summarize-doc` | 摘要文件 | Generate document summary | 生成文件摘要 | Low | 低 |
| `/search-content` | 搜尋內容 | Search within content | 搜尋內容 | Low | 低 |

### 4.2 File Commands | 檔案指令

| Command | 指令 | Description | 說明 | Risk | 風險 |
|---------|------|-------------|------|------|------|
| `/list-files` | 列出檔案 | List files in scope | 列出範圍內檔案 | Low | 低 |
| `/convert-file` | 轉換檔案 | Convert file format | 轉換檔案格式 | Low | 低 |
| `/delete-file` | 刪除檔案 | Delete file ⚠️ | 刪除檔案 | Critical | 嚴重 |

### 4.3 Deployment Commands | 部署指令

| Command | 指令 | Description | 說明 | Risk | 風險 |
|---------|------|-------------|------|------|------|
| `/generate-site` | 生成網站 | Generate static site | 生成靜態網站 | Medium | 中 |
| `/deploy-site` | 部署網站 | Deploy to production ⚠️ | 部署至生產環境 | High | 高 |

### 4.4 System Commands | 系統指令

| Command | 指令 | Description | 說明 | Risk | 風險 |
|---------|------|-------------|------|------|------|
| `/undo` | 恢復上一動 | Undo last action | 恢復上一操作 | Low | 低 |
| `/redo` | 重做 | Redo undone action | 重做被撤銷操作 | Low | 低 |
| `/history` | 歷史清單 | Show command history | 顯示指令歷史 | Low | 低 |

---

## 5. Technical Requirements | 技術需求

### 5.1 Environment | 環境

- **Python**: 3.11+
- **Dependencies**: pydantic>=2.0, pyyaml>=6.0, rich>=13.0

### 5.2 Architecture | 架構

```
src/
├── core/           # Core parsing engine | 核心解析引擎
├── mapping/        # Verb mapping | 動詞映射
├── sabe/           # S.A.B.E. protocol | S.A.B.E. 協議
├── progress_hacks/ # Five Hacks | 五言絕句 (NEW)
└── undo/           # Undo system | 恢復系統 (NEW)
```

---

## 6. Success Metrics | 成功指標

| Metric | 指標 | Target | 目標 |
|--------|------|--------|------|
| Parse accuracy | 解析準確率 | > 99% |
| Synonym coverage | 同義詞覆蓋 | > 85% common verbs |
| User satisfaction | 用戶滿意度 | > 4.5/5 |
| Zero destructive errors | 零破壞性錯誤 | 100% via S.A.B.E. |

---

## 7. Roadmap | 路線圖

### Phase 1: MVP (Current | 當前)
- [x] Core parser | 核心解析器
- [x] Verb mapping | 動詞映射
- [x] S.A.B.E. protocol | S.A.B.E. 協議
- [ ] Five Prompt Hacks | 五言絕句
- [ ] Undo/Redo system | 恢復/重做系統

### Phase 2: Enhancement | 增強
- [ ] LLM adapter integration | LLM 適配器整合
- [ ] Web UI | 網頁介面
- [ ] Plugin system | 插件系統

### Phase 3: Ecosystem | 生態系
- [ ] Team collaboration | 團隊協作
- [ ] Version control | 版本控制
- [ ] Marketplace | 市集

---

*Document maintained by SAD System Team*
