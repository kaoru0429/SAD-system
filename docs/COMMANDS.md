# Command Reference | 指令手冊

> Complete bilingual command reference for SAD System  
> SAD System 完整雙語指令參考

---

## Syntax Overview | 語法概覽

```
/verb-noun @input:id --param value
/動詞-名詞 @輸入:識別符 --參數 值
```

| Component | 組成 | Example | 範例 | Required | 必填 |
|-----------|------|---------|------|----------|------|
| Command | 指令 | `/analyze-data` | ✅ |
| Input | 輸入 | `@file:sales.csv` | Optional | 可選 |
| Parameters | 參數 | `--format markdown` | Optional | 可選 |

---

## Data Analysis Commands | 數據分析指令

### `/analyze-data` | 分析數據

**Description | 說明**: Perform detailed data analysis | 執行詳細數據分析

**Synonyms | 同義詞**: `analyze`, `inspect`, `examine`, `investigate`, `review`, `check`

```bash
# Full syntax | 完整語法
/analyze-data @file:sales.csv --type summary --format markdown

# Minimal | 最簡
/analyze-data @file:data.csv
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--type` | 類型 | `summary`, `detailed`, `statistical`, `trend` | `summary` |
| `--format` | 格式 | `markdown`, `json`, `html`, `csv` | `markdown` |

---

### `/summarize-doc` | 摘要文件

**Description | 說明**: Generate document summary | 生成文件摘要

**Synonyms | 同義詞**: `summarize`, `digest`, `condense`, `brief`, `abstract`, `outline`

```bash
/summarize-doc @file:report.pdf --length brief
/summarize-doc @url:https://example.com/article --length detailed
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--length` | 長度 | `brief`, `medium`, `detailed` | `medium` |
| `--format` | 格式 | `markdown`, `text`, `bullets` | `markdown` |

---

### `/search-content` | 搜尋內容

**Description | 說明**: Search within content | 搜尋內容

**Synonyms | 同義詞**: `search`, `find`, `locate`, `lookup`, `query`

```bash
/search-content @workspace:current --query "revenue 2024"
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--query` | 搜尋詞 | Any text | (required | 必填) |
| `--scope` | 範圍 | `all`, `files`, `data`, `history` | `all` |

---

## File Commands | 檔案指令

### `/list-files` | 列出檔案

**Description | 說明**: List files in directory or workspace | 列出目錄或工作區檔案

**Synonyms | 同義詞**: `list`, `show`, `display`, `enumerate`

```bash
/list-files @directory:./data --sort date
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--sort` | 排序 | `name`, `date`, `size`, `type` | `name` |
| `--filter` | 過濾 | Glob pattern | (none) |

---

### `/convert-file` | 轉換檔案

**Description | 說明**: Convert file format | 轉換檔案格式

**Synonyms | 同義詞**: `convert`, `transform`, `change`, `translate`

```bash
/convert-file @file:data.json --to csv --encoding utf-8
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--to` | 目標格式 | `json`, `csv`, `xml`, `yaml`, `markdown`, `html`, `pdf` | (required | 必填) |
| `--encoding` | 編碼 | `utf-8`, `ascii`, `big5` | `utf-8` |

---

### `/delete-file` | 刪除檔案 ⚠️

**Description | 說明**: Delete file or resource | 刪除檔案或資源

**Risk Level | 風險等級**: 🔴 Critical | 嚴重

**Synonyms | 同義詞**: `delete`, `remove`, `erase`, `destroy`

```bash
/delete-file @file:temp.txt --backup
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--force` | 強制 | `true`, `false` | `false` |
| `--backup` | 備份 | `true`, `false` | `true` |

> ⚠️ **Warning | 警告**: This command triggers S.A.B.E. confirmation | 此指令會觸發 S.A.B.E. 確認

---

## Deployment Commands | 部署指令

### `/generate-site` | 生成網站

**Description | 說明**: Generate static website | 生成靜態網站

**Synonyms | 同義詞**: `generate`, `create`, `build`, `make`, `produce`

```bash
/generate-site @file:content.md --template modern --style dark
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--template` | 模板 | `default`, `modern`, `minimal` | `default` |
| `--style` | 樣式 | `light`, `dark`, `auto` | `modern` |

---

### `/deploy-site` | 部署網站 ⚠️

**Description | 說明**: Deploy site to production | 部署網站至生產環境

**Risk Level | 風險等級**: 🔴 High | 高

**Synonyms | 同義詞**: `deploy`, `publish`, `release`, `launch`

```bash
/deploy-site @site:myapp --target production --backup
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--target` | 目標 | `staging`, `production` | (required | 必填) |
| `--backup` | 備份 | `true`, `false` | `true` |

> ⚠️ **Warning | 警告**: This command triggers S.A.B.E. confirmation | 此指令會觸發 S.A.B.E. 確認

---

## System Commands | 系統指令

### `/undo` | 恢復上一動 ⭐ NEW

**Description | 說明**: Undo last action | 恢復上一操作

```bash
# Undo last action | 恢復上一動
/undo

# Undo 3 steps | 恢復前三步
/undo --steps 3

# Preview what will be restored | 預覽將恢復內容
/undo --preview
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--steps` | 步數 | 1-10 | `1` |
| `--preview` | 預覽 | flag | - |

---

### `/redo` | 重做 ⭐ NEW

**Description | 說明**: Redo undone action | 重做被撤銷操作

```bash
/redo
/redo --steps 2
```

---

### `/history` | 歷史清單 ⭐ NEW

**Description | 說明**: Show command history | 顯示指令歷史

```bash
/history
/history --limit 20
```

**Parameters | 參數**:

| Param | 參數 | Values | 可選值 | Default | 預設 |
|-------|------|--------|--------|---------|------|
| `--limit` | 數量限制 | 1-100 | `10` |

---

## Input Types | 輸入類型

| Type | 類型 | Format | 格式 | Example | 範例 |
|------|------|--------|------|---------|------|
| File | 檔案 | `@file:filename` | `@file:sales.csv` |
| URL | 網址 | `@url:address` | `@url:https://example.com` |
| Data | 數據 | `@data:id` | `@data:q4-report` |
| Directory | 目錄 | `@directory:path` | `@directory:./docs` |
| Workspace | 工作區 | `@workspace:name` | `@workspace:current` |
| Site | 網站 | `@site:name` | `@site:myapp` |

---

## Quick Reference Card | 快速參考卡

```
┌─────────────────────────────────────────────────────────────┐
│ SAD System Command Quick Reference | 快速指令參考            │
├─────────────────────────────────────────────────────────────┤
│ DATA | 數據                                                  │
│   /analyze-data @file:X --format markdown                   │
│   /summarize-doc @file:X --length brief                     │
│   /search-content --query "keyword"                         │
├─────────────────────────────────────────────────────────────┤
│ FILES | 檔案                                                 │
│   /list-files --sort date                                   │
│   /convert-file @file:X --to csv                            │
│   /delete-file @file:X --backup  ⚠️                         │
├─────────────────────────────────────────────────────────────┤
│ DEPLOY | 部署                                                │
│   /generate-site @file:X --template modern                  │
│   /deploy-site @site:X --target production  ⚠️              │
├─────────────────────────────────────────────────────────────┤
│ SYSTEM | 系統                                                │
│   /undo --steps 3                                           │
│   /redo                                                     │
│   /history --limit 20                                       │
└─────────────────────────────────────────────────────────────┘
```

---

*SAD System - Strict Syntax, Lenient Vocabulary*  
*SAD System - 用法嚴格，用字寬容*
