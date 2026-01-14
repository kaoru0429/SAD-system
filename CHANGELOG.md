# Changelog
# 變更日誌

All notable changes to SAD System will be documented in this file.
所有 SAD System 的重要變更都會記錄在此文件中。

## [1.0.0] - 2026-01-14

### Added | 新增

#### Core Features | 核心功能
- **Command Parser** - Universal LLM command syntax parser
- **Verb Mapper** - Synonym mapping with confidence scoring
- **Command Registry** - Centralized command registration

#### S.A.B.E. Protocol | S.A.B.E. 協議
- Mode A: Ambiguous verb repair | 模糊動詞修復
- Mode B: Error recovery | 錯誤恢復
- Mode C: Large task confirmation | 大型任務確認
- Mode D: High risk confirmation | 高風險確認
- Mode E: Input missing | 輸入缺失

#### Five Prompt Hacks | 五言絕句
- 🎯 Clarify (20%) - Ask clarifying questions | 先澄清
- 🌐 Web-backed (40%) - Search for latest info | 網路查證
- 📊 Self-grade (60%) - Evaluate to 9/10 | 自我評分
- 👥 3-Expert Panel (80%) - Multi-perspective | 三專家觀點
- 😈 Devil's Advocate (100%) - Find blind spots | 自我批判

#### Undo System | 恢復系統
- `/undo` - Restore previous state | 恢復上一狀態
- `/undo --steps N` - Multi-step undo | 多步恢復
- `/undo --preview` - Preview changes | 預覽變更
- `/redo` - Redo undone actions | 重做
- `/history` - View command history | 查看歷史

#### Setup Wizard | 設定精靈
- First-run configuration | 首次執行配置
- 7 preset configurations | 7 種預設配置
- Custom hack selection | 自訂技巧選擇
- Persistent settings | 持久化設定

#### Integration | 整合
- SABE-Hacks integration layer | SABE-Hacks 整合層
- Automatic hack injection based on SABE mode | 基於 SABE 模式自動注入技巧
- Progress tracking with visual indicators | 進度追蹤與視覺指示

### Documentation | 文件
- Bilingual PRD (EN/中文)
- Bilingual command reference
- Bilingual SABE protocol specification
- Bilingual Five Hacks guide

### Testing | 測試
- 135 unit and integration tests
- 100% core feature coverage

---

## [0.1.0] - 2026-01-13

### Added | 新增
- Initial project structure
- Basic command parser
- Verb mapper prototype
- SABE protocol foundation
