# SAD System (SLASH@DASH Smart Command System)
# SAD 系統（智慧指令系統）

> **Strict Syntax, Lenient Vocabulary** - Universal LLM Command Interface  
> **用法嚴格，用字寬容** - 萬用 LLM 對話指令集

## 📋 Overview | 概述

**EN**: SAD (SLASH@DASH) is an intelligent LLM command system that bridges natural language and programmatic instructions through strict syntax structure and lenient semantic mapping.

**中文**: SAD (SLASH@DASH) 是一個智慧 LLM 指令系統，透過嚴格的語法結構與寬容的語意映射，實現自然語言到程式化指令的安全轉換。

### Core Features | 核心特色

- 🎯 **Strict Syntax | 嚴格語法** - Fixed command structure ensures stable parsing
- 🤝 **Lenient Vocabulary | 寬容語意** - Synonym mapping improves user experience
- 🛡️ **S.A.B.E. Protocol | S.A.B.E. 協議** - Suggest & Ask Before Exec ensures zero-error automation
- ✨ **Five Hacks | 五言絕句** - Auto-inject quality prompts at progress milestones
- ↩️ **Undo System | 恢復上一動** - Reversible operations for safety

## 🚀 Quick Start | 快速開始

```bash
# Install | 安裝
pip install sad-system

# Basic usage | 基本使用
from sad import CommandParser

parser = CommandParser()
result = parser.parse("/analyze-data @file:sales.csv --format markdown")
```

## 📖 Command Syntax | 指令語法

```
/verb-noun @input:id --param value
/動詞-名詞 @輸入:識別符 --參數 值
```

### Examples | 範例

```bash
# Data analysis | 數據分析
/analyze-data @file:sales.csv --type summary --format markdown

# Document summary | 文件摘要
/summarize-doc @file:report.pdf --length brief

# File conversion | 檔案轉換
/convert-file @file:data.json --to csv

# Undo last action | 恢復上一動
/undo --steps 1
```

## 🔧 Requirements | 安裝需求

- Python 3.11+
- Dependencies: `pydantic>=2.0`, `pyyaml>=6.0`, `rich>=13.0`

## 📚 Documentation | 文件

| Document | 文件 | Description | 說明 |
|----------|------|-------------|------|
| [PRD](docs/PRD.md) | 產品需求文件 | Product requirements | 產品需求 |
| [DESIGN](docs/DESIGN.md) | 設計文件 | Technical design | 技術設計 |
| [COMMANDS](docs/COMMANDS.md) | 指令手冊 | Command reference | 指令參考 |
| [SABE](docs/SABE.md) | S.A.B.E. 協議 | Safety protocol | 安全協議 |
| [FIVE_HACKS](docs/FIVE_HACKS.md) | 五言絕句 | Prompt enhancement | Prompt 增強 |

## 📄 License

MIT

---

*SAD System - Strict Syntax, Lenient Vocabulary | 用法嚴格，用字寬容*

