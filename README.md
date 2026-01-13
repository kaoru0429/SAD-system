# SAD System (SLASH@DASH 智慧指令系統)

> **用法嚴格，用字寬容** - 萬用 LLM 對話指令集

## 📋 概述

SAD (SLASH@DASH) 是一個智慧 LLM 指令系統，透過嚴格的語法結構與寬容的語意映射，實現自然語言到程式化指令的安全轉換。

### 核心特色

- 🎯 **嚴格語法** - 固定不變的指令結構確保系統穩定解析
- 🤝 **寬容語意** - 動詞同義詞智能映射提升用戶體驗
- 🛡️ **S.A.B.E. 協議** - Suggest & Ask Before Exec 確保零錯誤自動化

## 🚀 快速開始

```bash
# 安裝
pip install sad-system

# 基本使用
from sad import CommandParser

parser = CommandParser()
result = parser.parse("/analyze-data @file:sales.csv --format markdown")
```

## 📖 指令語法

```
/指令名 @輸入 --參數 值
```

### 範例

```bash
# 數據分析
/analyze-data @file:sales.csv --type summary --format markdown

# 文件摘要
/summarize-doc @file:report.pdf --length brief

# 檔案轉換
/convert-file @file:data.json --to csv
```

## 🔧 安裝需求

- Python 3.11+
- 依賴套件見 `requirements.txt`

## 📚 文件

- [設計文件](docs/DESIGN.md)
- [指令手冊](docs/COMMANDS.md)
- [S.A.B.E. 協議](docs/SABE.md)

## 📄 License

MIT
