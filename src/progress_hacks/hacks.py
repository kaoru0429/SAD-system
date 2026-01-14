"""
Prompt Hacks - 提示技巧定義

Defines the five prompt hacks and their postscripts.
定義五個提示技巧及其附言。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PromptHack:
    """
    提示技巧 | Prompt Hack
    
    Represents a single prompt hack with its postscript.
    代表單個提示技巧及其附言。
    
    Attributes:
        id: Unique identifier | 唯一識別符
        name_zh: Chinese name | 中文名稱
        name_en: English name | 英文名稱
        emoji: Display emoji | 顯示表情符號
        milestone: Progress percentage (20, 40, 60, 80, 100) | 進度百分比
        postscript: The prompt text to inject | 要注入的提示文字
        enabled: Whether this hack is enabled | 是否啟用
        use_when: Usage scenarios | 使用場景
    """
    id: str
    name_zh: str
    name_en: str
    emoji: str
    milestone: int
    postscript: str
    enabled: bool = True
    use_when: list[str] = field(default_factory=list)
    fallback: str | None = None
    enhanced: str | None = None
    
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        return f"{self.emoji} {self.name_en} | {self.name_zh}"
    
    @property
    def short_name(self) -> str:
        """Get short name with emoji."""
        return f"{self.emoji} {self.name_en}"
    
    def get_postscript(self, enhanced: bool = False) -> str:
        """
        Get the postscript text.
        取得附言文字。
        
        Args:
            enhanced: Use enhanced version if available | 使用增強版本（如果可用）
            
        Returns:
            Postscript text | 附言文字
        """
        if enhanced and self.enhanced:
            return f"{self.postscript.strip()}\n\n{self.enhanced.strip()}"
        return self.postscript.strip()
    
    def format_injection(self, style: str = "default") -> str:
        """
        Format the hack for injection into prompt.
        格式化技巧以注入到提示中。
        
        Args:
            style: Formatting style | 格式化樣式
            
        Returns:
            Formatted postscript | 格式化的附言
        """
        if style == "minimal":
            return self.postscript.strip()
        
        if style == "boxed":
            return f"""
╭─────────────────────────────────────────────────────╮
│ {self.display_name:^51} │
├─────────────────────────────────────────────────────┤
│                                                     │
{self._wrap_text(self.postscript, 51)}
│                                                     │
╰─────────────────────────────────────────────────────╯
"""
        
        # Default style
        return f"""
{self.display_name}
{'─' * 40}
{self.postscript.strip()}
"""
    
    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text for box display."""
        lines = []
        for line in text.strip().split('\n'):
            while len(line) > width - 4:
                lines.append(f"│ {line[:width-4]} │")
                line = line[width-4:]
            lines.append(f"│ {line:<{width-4}} │")
        return '\n'.join(lines)
    
    def __str__(self) -> str:
        status = "✓" if self.enabled else "○"
        return f"{status} {self.milestone}% {self.display_name}"


# Default hacks definition
DEFAULT_HACKS: list[dict[str, Any]] = [
    {
        "id": "clarify",
        "name_zh": "先澄清",
        "name_en": "Clarify",
        "emoji": "🎯",
        "milestone": 20,
        "enabled": True,
        "postscript": "Ask me clarifying questions until you are 95% confident you understand what I want before generating the final output.",
        "use_when": [
            "Task has hidden preferences (tone, audience, constraints)",
            "Wrong assumptions would waste time"
        ]
    },
    {
        "id": "web_backed",
        "name_zh": "網路查證",
        "name_en": "Web-backed",
        "emoji": "🌐",
        "milestone": 40,
        "enabled": True,
        "postscript": "Before answering, search the web for the most recent and credible information. Include sources and a timestamp.",
        "use_when": [
            "Time-sensitive data (pricing, laws, product features)",
            "You want receipts, not vibes"
        ],
        "fallback": "If you cannot browse, tell me exactly what you would search for, which sources you would trust most, and what might be outdated."
    },
    {
        "id": "self_grade",
        "name_zh": "自我評分",
        "name_en": "Self-grade",
        "emoji": "📊",
        "milestone": 60,
        "enabled": True,
        "postscript": "Before answering, evaluate your answer for accuracy, completeness, usefulness, and clarity until it is at least 9 out of 10 in each category.",
        "use_when": [
            "Need polished deliverable (strategy, pitch, SOP)",
            "Hate re-prompting for obvious fixes"
        ]
    },
    {
        "id": "expert_panel",
        "name_zh": "三專家觀點",
        "name_en": "3-Expert Panel",
        "emoji": "👥",
        "milestone": 80,
        "enabled": False,  # Disabled by default, heavier weight
        "postscript": "Answer using a 3-expert panel: a practitioner, a skeptic, and an editor. Show where they disagree, then synthesize one final answer with the best tradeoffs.",
        "use_when": [
            "Making decisions and want tradeoffs",
            "Want fewer blind spots"
        ]
    },
    {
        "id": "devils_advocate",
        "name_zh": "自我批判",
        "name_en": "Devil's Advocate",
        "emoji": "😈",
        "milestone": 100,
        "enabled": True,
        "postscript": "After generating your answer, provide a critique of your own response from the perspective of a skeptic. Highlight potential biases, missing angles, or logical gaps.",
        "use_when": [
            "Brainstorming, decision-making, sanity-checking",
            "Want to catch weak logic before acting"
        ],
        "enhanced": "Assume my plan fails. List the top 10 reasons and how to mitigate each."
    }
]


def load_hacks(config_path: str | Path | None = None) -> list[PromptHack]:
    """
    Load prompt hacks from config or use defaults.
    從配置載入提示技巧或使用預設值。
    
    Args:
        config_path: Path to hacks.yaml | hacks.yaml 的路徑
        
    Returns:
        List of PromptHack instances | PromptHack 實例列表
    """
    hacks_data = DEFAULT_HACKS
    
    if config_path:
        path = Path(config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config and "hacks" in config:
                    hacks_data = list(config["hacks"].values())
    
    return [PromptHack(**data) for data in hacks_data]


def get_hack_by_id(hacks: list[PromptHack], hack_id: str) -> PromptHack | None:
    """Get a specific hack by ID."""
    for hack in hacks:
        if hack.id == hack_id:
            return hack
    return None


def get_hack_by_milestone(hacks: list[PromptHack], milestone: int) -> PromptHack | None:
    """Get hack for a specific milestone."""
    for hack in hacks:
        if hack.milestone == milestone and hack.enabled:
            return hack
    return None


def get_enabled_hacks(hacks: list[PromptHack]) -> list[PromptHack]:
    """Get only enabled hacks."""
    return [h for h in hacks if h.enabled]
