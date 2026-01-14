"""
Progress Tracker - 進度追蹤器

Tracks task progress and determines when to inject hacks.
追蹤任務進度並決定何時注入技巧。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
from datetime import datetime

from .hacks import PromptHack, load_hacks, get_hack_by_milestone


class MilestoneStatus(Enum):
    """里程碑狀態 | Milestone Status"""
    PENDING = "pending"       # 待處理 | Pending
    REACHED = "reached"       # 已到達 | Reached  
    INJECTED = "injected"     # 已注入 | Injected
    SKIPPED = "skipped"       # 已跳過 | Skipped


@dataclass
class Milestone:
    """
    里程碑 | Milestone
    
    Represents a progress milestone with its associated hack.
    代表一個進度里程碑及其關聯的技巧。
    """
    percentage: int
    hack: PromptHack | None
    status: MilestoneStatus = MilestoneStatus.PENDING
    reached_at: datetime | None = None
    injected_at: datetime | None = None
    
    @property
    def indicator(self) -> str:
        """Get status indicator."""
        if self.status == MilestoneStatus.INJECTED:
            return "●"
        elif self.status == MilestoneStatus.REACHED:
            return "◐"
        elif self.status == MilestoneStatus.SKIPPED:
            return "○"
        return "○"
    
    @property
    def emoji(self) -> str:
        """Get hack emoji or placeholder."""
        return self.hack.emoji if self.hack else "○"
    
    def mark_reached(self) -> None:
        """Mark milestone as reached."""
        self.status = MilestoneStatus.REACHED
        self.reached_at = datetime.now()
    
    def mark_injected(self) -> None:
        """Mark milestone as injected."""
        self.status = MilestoneStatus.INJECTED
        self.injected_at = datetime.now()
    
    def mark_skipped(self) -> None:
        """Mark milestone as skipped."""
        self.status = MilestoneStatus.SKIPPED


@dataclass
class ProgressState:
    """
    Progress state container.
    進度狀態容器。
    """
    current: int = 0
    total: int = 100
    milestones: list[Milestone] = field(default_factory=list)
    last_milestone_reached: int = 0
    
    @property
    def percentage(self) -> float:
        """Get current progress percentage."""
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100


class ProgressTracker:
    """
    進度追蹤器 | Progress Tracker
    
    Tracks task progress and manages milestone-based hack injection.
    追蹤任務進度並管理基於里程碑的技巧注入。
    
    Example:
        >>> tracker = ProgressTracker()
        >>> tracker.set_total(100)
        >>> hack = tracker.update_progress(25)
        >>> if hack:
        ...     print(f"Inject: {hack.display_name}")
    """
    
    MILESTONE_POINTS = [20, 40, 60, 80, 100]
    
    def __init__(
        self,
        hacks: list[PromptHack] | None = None,
        on_milestone: Callable[[Milestone], None] | None = None
    ) -> None:
        """
        Initialize progress tracker.
        初始化進度追蹤器。
        
        Args:
            hacks: List of prompt hacks | 提示技巧列表
            on_milestone: Callback when milestone reached | 到達里程碑時的回調
        """
        self._hacks = hacks or load_hacks()
        self._on_milestone = on_milestone
        self._state = ProgressState()
        self._setup_milestones()
    
    def _setup_milestones(self) -> None:
        """Initialize milestones with hacks."""
        self._state.milestones = []
        for pct in self.MILESTONE_POINTS:
            hack = get_hack_by_milestone(self._hacks, pct)
            self._state.milestones.append(Milestone(percentage=pct, hack=hack))
    
    def set_total(self, total: int) -> None:
        """
        Set total progress units.
        設定總進度單位。
        
        Args:
            total: Total units | 總單位數
        """
        self._state.total = total
        self._state.current = 0
        self._state.last_milestone_reached = 0
        self._setup_milestones()
    
    def update_progress(self, current: int) -> PromptHack | None:
        """
        Update progress and check for milestone.
        更新進度並檢查里程碑。
        
        Args:
            current: Current progress value | 當前進度值
            
        Returns:
            PromptHack if milestone reached, None otherwise
            如果到達里程碑則返回 PromptHack，否則返回 None
        """
        self._state.current = current
        percentage = self._state.percentage
        
        # Check each milestone
        for milestone in self._state.milestones:
            if milestone.status != MilestoneStatus.PENDING:
                continue
            
            if percentage >= milestone.percentage:
                milestone.mark_reached()
                
                if self._on_milestone:
                    self._on_milestone(milestone)
                
                if milestone.hack and milestone.hack.enabled:
                    return milestone.hack
        
        return None
    
    def increment_progress(self, amount: int = 1) -> PromptHack | None:
        """
        Increment progress by amount.
        按量增加進度。
        
        Args:
            amount: Amount to increment | 增加量
            
        Returns:
            PromptHack if milestone reached | 如果到達里程碑則返回 PromptHack
        """
        return self.update_progress(self._state.current + amount)
    
    def mark_injected(self, milestone_pct: int) -> None:
        """
        Mark a milestone as injected.
        標記里程碑已注入。
        
        Args:
            milestone_pct: Milestone percentage | 里程碑百分比
        """
        for milestone in self._state.milestones:
            if milestone.percentage == milestone_pct:
                milestone.mark_injected()
                break
    
    def skip_milestone(self, milestone_pct: int) -> None:
        """
        Skip a milestone.
        跳過里程碑。
        
        Args:
            milestone_pct: Milestone percentage | 里程碑百分比
        """
        for milestone in self._state.milestones:
            if milestone.percentage == milestone_pct:
                milestone.mark_skipped()
                break
    
    def get_progress_indicator(self) -> str:
        """
        Get visual progress indicator with lights.
        取得帶燈號的視覺進度指示器。
        
        Returns:
            Formatted progress indicator string | 格式化的進度指示器字串
        """
        emojis = " ".join(m.emoji for m in self._state.milestones)
        indicators = " ".join(f" {m.indicator} " for m in self._state.milestones)
        percentages = " ".join(f"{m.percentage:>3}%" for m in self._state.milestones)
        
        current_pct = int(self._state.percentage)
        
        return f"""
┌─────────────────────────────────────────┐
│ 📊 Task Progress | 任務進度 [{current_pct:>3}%]      │
│                                         │
│  {emojis}                     │
│  {indicators}                    │
│ {percentages}                │
└─────────────────────────────────────────┘
"""
    
    def get_compact_indicator(self) -> str:
        """
        Get compact one-line progress indicator.
        取得緊湊的單行進度指示器。
        
        Returns:
            Compact indicator string | 緊湊的指示器字串
        """
        parts = []
        for m in self._state.milestones:
            parts.append(f"{m.emoji}{m.indicator}")
        
        current_pct = int(self._state.percentage)
        return f"[{current_pct}%] " + " ".join(parts)
    
    def get_injected_count(self) -> int:
        """Get number of injected milestones."""
        return sum(1 for m in self._state.milestones if m.status == MilestoneStatus.INJECTED)
    
    def get_remaining_count(self) -> int:
        """Get number of remaining milestones."""
        return sum(1 for m in self._state.milestones if m.status == MilestoneStatus.PENDING)
    
    @property
    def current_percentage(self) -> float:
        """Get current progress percentage."""
        return self._state.percentage
    
    @property
    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self._state.percentage >= 100
    
    def reset(self) -> None:
        """Reset tracker to initial state."""
        self._state.current = 0
        self._state.last_milestone_reached = 0
        self._setup_milestones()
