"""
Presets - 預設配置

Predefined configurations for different use cases.
針對不同使用場景的預定義配置。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PresetType(Enum):
    """預設類型 | Preset Type"""
    RECOMMENDED = "recommended"  # 推薦 (排除 expert_panel)
    ALL = "all"                  # 全部啟用
    ANALYSIS = "analysis"        # 分析場景
    RESEARCH = "research"        # 研究場景
    WRITING = "writing"          # 寫作場景
    MINIMAL = "minimal"          # 最小化
    NONE = "none"                # 全部禁用


@dataclass
class Preset:
    """
    預設配置 | Preset Configuration
    
    Defines which hacks are enabled for a specific use case.
    定義特定使用場景啟用哪些 hack。
    """
    id: str
    name_zh: str
    name_en: str
    description_zh: str
    description_en: str
    enabled_hacks: list[str]
    icon: str = "⚙️"
    
    @property
    def display_name(self) -> str:
        """Get bilingual display name."""
        return f"{self.icon} {self.name_en} | {self.name_zh}"
    
    @property
    def description(self) -> str:
        """Get bilingual description."""
        return f"{self.description_en} | {self.description_zh}"
    
    def get_enabled_emojis(self) -> str:
        """Get emoji representation of enabled hacks."""
        emoji_map = {
            "clarify": "🎯",
            "web_backed": "🌐",
            "self_grade": "📊",
            "expert_panel": "👥",
            "devils_advocate": "😈",
        }
        return " ".join(emoji_map.get(h, "○") for h in self.enabled_hacks)


# Default presets
DEFAULT_PRESETS: list[Preset] = [
    Preset(
        id="recommended",
        name_zh="推薦",
        name_en="Recommended",
        description_zh="平衡品質與速度",
        description_en="Balance quality and speed",
        icon="⭐",
        enabled_hacks=["clarify", "web_backed", "self_grade", "devils_advocate"]
    ),
    Preset(
        id="all",
        name_zh="全部",
        name_en="All",
        description_zh="啟用所有五種技巧",
        description_en="Enable all five hacks",
        icon="🔥",
        enabled_hacks=["clarify", "web_backed", "self_grade", "expert_panel", "devils_advocate"]
    ),
    Preset(
        id="analysis",
        name_zh="分析",
        name_en="Analysis",
        description_zh="適合數據分析任務",
        description_en="For data analysis tasks",
        icon="📊",
        enabled_hacks=["clarify", "self_grade"]
    ),
    Preset(
        id="research",
        name_zh="研究",
        name_en="Research",
        description_zh="需要最新資訊與多角度",
        description_en="Need latest info & perspectives",
        icon="🔍",
        enabled_hacks=["web_backed", "expert_panel", "devils_advocate"]
    ),
    Preset(
        id="writing",
        name_zh="寫作",
        name_en="Writing",
        description_zh="追求高品質輸出",
        description_en="High quality output",
        icon="✍️",
        enabled_hacks=["self_grade", "devils_advocate"]
    ),
    Preset(
        id="minimal",
        name_zh="最小化",
        name_en="Minimal",
        description_zh="僅啟用先澄清",
        description_en="Only clarify",
        icon="💨",
        enabled_hacks=["clarify"]
    ),
    Preset(
        id="none",
        name_zh="跳過",
        name_en="Skip",
        description_zh="不啟用任何技巧",
        description_en="No hacks enabled",
        icon="⏭️",
        enabled_hacks=[]
    ),
]


def get_presets() -> list[Preset]:
    """
    Get all available presets.
    取得所有可用的預設。
    
    Returns:
        List of Preset objects | Preset 物件列表
    """
    return DEFAULT_PRESETS.copy()


def get_preset_by_id(preset_id: str) -> Preset | None:
    """
    Get preset by ID.
    根據 ID 取得預設。
    
    Args:
        preset_id: Preset identifier | 預設識別符
        
    Returns:
        Preset or None if not found | 預設或 None
    """
    for preset in DEFAULT_PRESETS:
        if preset.id == preset_id:
            return preset
    return None


def get_recommended_preset() -> Preset:
    """
    Get the recommended preset.
    取得推薦的預設。
    
    Returns:
        Recommended Preset | 推薦的預設
    """
    return get_preset_by_id("recommended") or DEFAULT_PRESETS[0]
