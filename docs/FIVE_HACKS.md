# Five Prompt Hacks | 五言絕句

> Auto-inject quality-enhancing prompts at progress milestones  
> 在進度里程碑自動注入品質提升附言

---

## Overview | 概述

**EN**: Five Prompt Hacks is an intelligent prompt enhancement system that automatically injects proven prompt techniques at specific progress milestones during task execution.

**中文**: 五言絕句是一個智能 prompt 增強系統，在任務執行的特定進度里程碑自動注入經驗證的 prompt 技巧。

---

## The Five Hacks | 五言絕句對照表

### 🎯 Hack 1: Clarify | 先澄清 (20%)

**Postscript | 附言**:
```
Ask me clarifying questions until you are 95% confident you 
understand what I want before generating the final output.
```

**Use when | 適用場景**:
- Task has hidden preferences (tone, audience, constraints)
- 任務有隱藏偏好（語氣、受眾、限制）
- Wrong assumptions would waste time
- 錯誤假設會浪費時間

**Why it works | 原理**: Most bad answers come from missing context. This forces the model to ask instead of guess.

---

### 🌐 Hack 2: Web-backed | 網路查證 (40%)

**Postscript | 附言**:
```
Before answering, search the web for the most recent and 
credible information. Include sources and a timestamp.
```

**Use when | 適用場景**:
- Time-sensitive data (pricing, laws, product features, news)
- 時效性資料（價格、法規、產品、新聞）
- You want receipts, not vibes
- 你需要來源，不是臆測

**Why it works | 原理**: Models can be stale. This forces a recency check.

---

### 📊 Hack 3: Self-grade | 自我評分 (60%)

**Postscript | 附言**:
```
Before answering, evaluate your answer for accuracy, completeness, 
usefulness, and clarity until it is at least 9 out of 10 in each category.
```

**Use when | 適用場景**:
- Need polished deliverable (strategy, pitch, SOP)
- 需要精緻交付物（策略、簡報、SOP）
- Hate re-prompting for obvious fixes
- 討厭為顯而易見的問題重新提問

**Why it works | 原理**: First drafts are fine. Second drafts are where quality jumps.

---

### 👥 Hack 4: 3-Expert Panel | 三專家觀點 (80%)

**Postscript | 附言**:
```
Answer using a 3-expert panel: a practitioner, a skeptic, and an editor. 
Show where they disagree, then synthesize one final answer with the best tradeoffs.
```

**Use when | 適用場景**:
- Making decisions and want tradeoffs
- 做決策時需要權衡
- Want fewer blind spots
- 想要減少盲點

**Why it works | 原理**: One voice gives one angle. Three voices surfaces tradeoffs.

---

### 😈 Hack 5: Devil's Advocate | 自我批判 (~100%)

**Postscript | 附言**:
```
After generating your answer, provide a critique of your own response 
from the perspective of a skeptic. Highlight potential biases, 
missing angles, or logical gaps.
```

**Use when | 適用場景**:
- Brainstorming, decision-making, sanity-checking
- 腦力激盪、決策制定、理智檢查
- Want to catch weak logic before acting
- 想在行動前發現邏輯漏洞

**Why it works | 原理**: Most AI outputs sound confident even when incomplete.

---

## Progress Indicator UI | 進度燈號介面

```
┌─────────────────────────────────────────┐
│ 📊 Task Progress | 任務進度              │
│                                         │
│  🎯  🌐  📊  👥  😈                     │
│  ●   ●   ○   ○   ○                     │
│ 20% 40% 60% 80% 100%                   │
│                                         │
│ ✓ Clarify injected | 已注入先澄清        │
│ ✓ Web-backed injected | 已注入網路查證   │
└─────────────────────────────────────────┘
```

**Legend | 圖例**:
- `●` = Completed & injected | 已完成並注入
- `○` = Pending | 待處理

---

## First-Run Setup | 首次設定

On first conversation, users can configure which hacks to enable:
首次對話時，用戶可設定要啟用哪些 hack：

```
🔧 Five Hacks Setup | 五言絕句設定

Select hacks to enable | 選擇要啟用的 Hack：

[x] 1. 🎯 Clarify (20%) - Ask clarifying questions | 先問澄清問題
[x] 2. 🌐 Web-backed (40%) - Search recent info | 搜尋最新資訊  
[x] 3. 📊 Self-grade (60%) - Iterate to 9/10 | 迭代至 9/10
[ ] 4. 👥 3-Expert (80%) - Multi-perspective | 多角度觀點
[x] 5. 😈 Devil's Advocate (~100%) - Self-critique | 自我批判

> Toggle 1-5, or Enter to confirm | 輸入 1-5 切換，Enter 確認
```

---

## Configuration | 配置

```yaml
# config/hacks.yaml
hacks:
  clarify:
    enabled: true
    milestone: 20
    postscript: "Ask me clarifying questions until you are 95% confident..."
    
  web_backed:
    enabled: true
    milestone: 40
    postscript: "Before answering, search the web for the most recent..."
    
  self_grade:
    enabled: true
    milestone: 60
    postscript: "Before answering, evaluate your answer for accuracy..."
    
  expert_panel:
    enabled: false
    milestone: 80
    postscript: "Answer using a 3-expert panel..."
    
  devils_advocate:
    enabled: true
    milestone: 100
    postscript: "After generating your answer, provide a critique..."
```

---

## Integration with S.A.B.E. | 與 S.A.B.E. 整合

Five Hacks works alongside S.A.B.E. protocol:
五言絕句與 S.A.B.E. 協議協同工作：

| Scenario | 場景 | Behavior | 行為 |
|----------|------|----------|------|
| S.A.B.E. Mode A (Ambiguous) | 模糊修復 | Clarify hack auto-suggested | 自動建議先澄清 |
| S.A.B.E. Mode C (Large Task) | 大型任務 | All hacks recommended | 建議啟用全部 |
| S.A.B.E. Mode D (High Risk) | 高風險 | Devil's Advocate enforced | 強制自我批判 |

---

## Why This Works | 為何有效

> "You are not improving the question, you are improving the workflow."
> 「你不是在改善問題，你是在改善工作流程。」

These postscripts force:
這些附言強制執行：

1. **Clarification** | 澄清 - Ask before guessing
2. **Recency** | 時效 - Check latest information
3. **Iteration** | 迭代 - Polish before delivering
4. **Multi-angle** | 多角度 - Consider tradeoffs
5. **Skepticism** | 懷疑 - Find blind spots

---

*Five Hacks - Automated Prompt Excellence*  
*五言絕句 - 自動化的卓越 Prompt*
