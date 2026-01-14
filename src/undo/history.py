"""
History Stack - 歷史堆疊

Manages the undo/redo history stack with configurable limits.
管理具有可配置限制的恢復/重做歷史堆疊。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Iterator
from datetime import datetime

from .snapshots import CommandSnapshot, AnySnapshot


@dataclass
class HistoryConfig:
    """
    History configuration | 歷史配置
    
    Attributes:
        max_history: Maximum snapshots to keep | 保留的最大快照數
        auto_cleanup: Auto cleanup old entries | 自動清理舊條目
        persist: Persist to disk | 持久化到磁碟
    """
    max_history: int = 100
    auto_cleanup: bool = True
    persist: bool = False
    persist_path: str | None = None


class HistoryStack:
    """
    歷史堆疊 | History Stack
    
    Manages command history with undo/redo stacks.
    管理具有恢復/重做堆疊的指令歷史。
    
    Example:
        >>> history = HistoryStack(max_size=50)
        >>> history.push(snapshot)
        >>> history.undo()  # Returns the snapshot to undo
        >>> history.redo()  # Returns the snapshot to redo
    """
    
    def __init__(self, config: HistoryConfig | None = None) -> None:
        """
        Initialize history stack.
        初始化歷史堆疊。
        
        Args:
            config: History configuration | 歷史配置
        """
        self._config = config or HistoryConfig()
        self._undo_stack: deque[AnySnapshot] = deque(maxlen=self._config.max_history)
        self._redo_stack: deque[AnySnapshot] = deque()
        self._current_index: int = -1
    
    def push(self, snapshot: AnySnapshot) -> None:
        """
        Push a new snapshot to history.
        將新快照推入歷史。
        
        Note: Clears redo stack when new command is added.
        注意：新增指令時會清除重做堆疊。
        
        Args:
            snapshot: Snapshot to add | 要新增的快照
        """
        self._undo_stack.append(snapshot)
        self._redo_stack.clear()  # Clear redo on new action
        self._current_index = len(self._undo_stack) - 1
    
    def undo(self) -> AnySnapshot | None:
        """
        Pop and return the last snapshot for undo.
        彈出並返回最後一個快照以供恢復。
        
        Returns:
            Snapshot to undo, or None if empty | 要恢復的快照，如果為空則返回 None
        """
        if not self._undo_stack:
            return None
        
        snapshot = self._undo_stack.pop()
        self._redo_stack.append(snapshot)
        self._current_index = len(self._undo_stack) - 1
        return snapshot
    
    def undo_steps(self, steps: int = 1) -> list[AnySnapshot]:
        """
        Undo multiple steps.
        恢復多個步驟。
        
        Args:
            steps: Number of steps to undo | 要恢復的步驟數
            
        Returns:
            List of snapshots undone | 已恢復的快照列表
        """
        undone: list[AnySnapshot] = []
        for _ in range(min(steps, len(self._undo_stack))):
            snapshot = self.undo()
            if snapshot:
                undone.append(snapshot)
        return undone
    
    def redo(self) -> AnySnapshot | None:
        """
        Pop and return snapshot for redo.
        彈出並返回快照以供重做。
        
        Returns:
            Snapshot to redo, or None if empty | 要重做的快照，如果為空則返回 None
        """
        if not self._redo_stack:
            return None
        
        snapshot = self._redo_stack.pop()
        self._undo_stack.append(snapshot)
        self._current_index = len(self._undo_stack) - 1
        return snapshot
    
    def redo_steps(self, steps: int = 1) -> list[AnySnapshot]:
        """
        Redo multiple steps.
        重做多個步驟。
        
        Args:
            steps: Number of steps to redo | 要重做的步驟數
            
        Returns:
            List of snapshots redone | 已重做的快照列表
        """
        redone: list[AnySnapshot] = []
        for _ in range(min(steps, len(self._redo_stack))):
            snapshot = self.redo()
            if snapshot:
                redone.append(snapshot)
        return redone
    
    def peek_undo(self) -> AnySnapshot | None:
        """
        Peek at the next undo snapshot without removing.
        查看下一個恢復快照而不移除。
        
        Returns:
            Next snapshot to undo | 下一個要恢復的快照
        """
        return self._undo_stack[-1] if self._undo_stack else None
    
    def peek_redo(self) -> AnySnapshot | None:
        """
        Peek at the next redo snapshot without removing.
        查看下一個重做快照而不移除。
        
        Returns:
            Next snapshot to redo | 下一個要重做的快照
        """
        return self._redo_stack[-1] if self._redo_stack else None
    
    def get_history(self, limit: int | None = None) -> list[AnySnapshot]:
        """
        Get history list (most recent first).
        取得歷史列表（最近的優先）。
        
        Args:
            limit: Maximum entries to return | 返回的最大條目數
            
        Returns:
            List of snapshots | 快照列表
        """
        history = list(reversed(self._undo_stack))
        if limit:
            history = history[:limit]
        return history
    
    def get_preview(self, steps: int = 1) -> list[AnySnapshot]:
        """
        Preview what will be undone.
        預覽將被恢復的內容。
        
        Args:
            steps: Number of steps to preview | 要預覽的步驟數
            
        Returns:
            List of snapshots that will be undone | 將被恢復的快照列表
        """
        preview_count = min(steps, len(self._undo_stack))
        return [self._undo_stack[-(i+1)] for i in range(preview_count)]
    
    def clear(self) -> None:
        """
        Clear all history.
        清除所有歷史。
        """
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._current_index = -1
    
    def clear_redo(self) -> None:
        """
        Clear only redo stack.
        僅清除重做堆疊。
        """
        self._redo_stack.clear()
    
    @property
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self._undo_stack) > 0
    
    @property
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self._redo_stack) > 0
    
    @property
    def undo_count(self) -> int:
        """Get number of undoable items."""
        return len(self._undo_stack)
    
    @property
    def redo_count(self) -> int:
        """Get number of redoable items."""
        return len(self._redo_stack)
    
    @property
    def is_empty(self) -> bool:
        """Check if history is empty."""
        return len(self._undo_stack) == 0 and len(self._redo_stack) == 0
    
    def __len__(self) -> int:
        """Get total history size."""
        return len(self._undo_stack) + len(self._redo_stack)
    
    def __iter__(self) -> Iterator[AnySnapshot]:
        """Iterate over undo stack (oldest first)."""
        return iter(self._undo_stack)
    
    def __repr__(self) -> str:
        return f"HistoryStack(undo={self.undo_count}, redo={self.redo_count})"


# Global history instance | 全域歷史實例
_global_history: HistoryStack | None = None


def get_history() -> HistoryStack:
    """
    Get global history stack instance.
    取得全域歷史堆疊實例。
    
    Returns:
        Global HistoryStack instance | 全域 HistoryStack 實例
    """
    global _global_history
    if _global_history is None:
        _global_history = HistoryStack()
    return _global_history


def reset_history(config: HistoryConfig | None = None) -> HistoryStack:
    """
    Reset global history with new config.
    用新配置重置全域歷史。
    
    Args:
        config: New configuration | 新配置
        
    Returns:
        New HistoryStack instance | 新的 HistoryStack 實例
    """
    global _global_history
    _global_history = HistoryStack(config)
    return _global_history
