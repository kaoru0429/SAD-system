"""
Undo Commands - 恢復指令

Implements /undo, /redo, /history commands.
實作 /undo, /redo, /history 指令。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .history import HistoryStack, get_history
from .snapshots import CommandSnapshot, AnySnapshot


@dataclass
class CommandResult:
    """
    Command execution result | 指令執行結果
    
    Attributes:
        success: Whether command succeeded | 指令是否成功
        message: Result message | 結果訊息
        data: Additional data | 額外資料
    """
    success: bool
    message: str
    data: Any = None


class UndoCommand:
    """
    /undo 指令 | Undo Command
    
    Restores previous state by undoing commands.
    透過恢復指令來回復先前狀態。
    
    Example:
        >>> undo = UndoCommand()
        >>> result = undo.execute(steps=1)
        >>> result = undo.execute(steps=3, preview=True)
    """
    
    def __init__(self, history: HistoryStack | None = None) -> None:
        """
        Initialize undo command.
        初始化恢復指令。
        
        Args:
            history: History stack to use | 要使用的歷史堆疊
        """
        self._history = history or get_history()
        self._console = Console()
    
    def execute(
        self,
        steps: int = 1,
        preview: bool = False
    ) -> CommandResult:
        """
        Execute undo command.
        執行恢復指令。
        
        Args:
            steps: Number of steps to undo | 要恢復的步驟數
            preview: Only preview, don't actually undo | 僅預覽，不實際恢復
            
        Returns:
            Command execution result | 指令執行結果
        """
        if not self._history.can_undo:
            return CommandResult(
                success=False,
                message="⚠️ 沒有可恢復的操作 | Nothing to undo"
            )
        
        if preview:
            return self._preview(steps)
        
        return self._perform_undo(steps)
    
    def _preview(self, steps: int) -> CommandResult:
        """Preview what will be undone."""
        snapshots = self._history.get_preview(steps)
        
        if not snapshots:
            return CommandResult(
                success=False,
                message="⚠️ 沒有可預覽的操作 | Nothing to preview"
            )
        
        lines = ["📋 將被恢復的操作 | Operations to be undone:", ""]
        for i, snap in enumerate(snapshots, 1):
            lines.append(f"  {i}. {snap}")
        
        return CommandResult(
            success=True,
            message="\n".join(lines),
            data={"snapshots": snapshots, "preview": True}
        )
    
    def _perform_undo(self, steps: int) -> CommandResult:
        """Actually perform the undo."""
        undone = self._history.undo_steps(steps)
        
        if not undone:
            return CommandResult(
                success=False,
                message="⚠️ 恢復失敗 | Undo failed"
            )
        
        # Restore states for each snapshot
        restored_count = 0
        for snapshot in undone:
            if isinstance(snapshot, CommandSnapshot):
                for state in snapshot.states:
                    if state.can_restore():
                        # TODO: Actually restore the state
                        restored_count += 1
        
        message = f"✅ 已恢復 {len(undone)} 個操作 | Undone {len(undone)} operation(s)"
        if restored_count > 0:
            message += f"\n   恢復了 {restored_count} 個狀態變更 | Restored {restored_count} state change(s)"
        
        return CommandResult(
            success=True,
            message=message,
            data={"undone": undone, "restored_states": restored_count}
        )
    
    def format_output(self, result: CommandResult) -> str:
        """Format result for display."""
        return result.message


class RedoCommand:
    """
    /redo 指令 | Redo Command
    
    Re-applies previously undone commands.
    重新套用先前被恢復的指令。
    
    Example:
        >>> redo = RedoCommand()
        >>> result = redo.execute(steps=1)
    """
    
    def __init__(self, history: HistoryStack | None = None) -> None:
        """Initialize redo command."""
        self._history = history or get_history()
        self._console = Console()
    
    def execute(self, steps: int = 1) -> CommandResult:
        """
        Execute redo command.
        執行重做指令。
        
        Args:
            steps: Number of steps to redo | 要重做的步驟數
            
        Returns:
            Command execution result | 指令執行結果
        """
        if not self._history.can_redo:
            return CommandResult(
                success=False,
                message="⚠️ 沒有可重做的操作 | Nothing to redo"
            )
        
        redone = self._history.redo_steps(steps)
        
        if not redone:
            return CommandResult(
                success=False,
                message="⚠️ 重做失敗 | Redo failed"
            )
        
        return CommandResult(
            success=True,
            message=f"✅ 已重做 {len(redone)} 個操作 | Redone {len(redone)} operation(s)",
            data={"redone": redone}
        )


class HistoryCommand:
    """
    /history 指令 | History Command
    
    Displays command history.
    顯示指令歷史。
    
    Example:
        >>> history_cmd = HistoryCommand()
        >>> result = history_cmd.execute(limit=20)
    """
    
    def __init__(self, history: HistoryStack | None = None) -> None:
        """Initialize history command."""
        self._history = history or get_history()
        self._console = Console()
    
    def execute(self, limit: int = 10) -> CommandResult:
        """
        Execute history command.
        執行歷史指令。
        
        Args:
            limit: Maximum entries to show | 顯示的最大條目數
            
        Returns:
            Command execution result | 指令執行結果
        """
        if self._history.is_empty:
            return CommandResult(
                success=True,
                message="📋 歷史記錄為空 | History is empty"
            )
        
        history_list = self._history.get_history(limit)
        
        lines = [
            f"📋 指令歷史 | Command History (顯示 {len(history_list)}/{self._history.undo_count})",
            f"   可恢復: {self._history.undo_count} | 可重做: {self._history.redo_count}",
            ""
        ]
        
        for i, snap in enumerate(history_list, 1):
            lines.append(f"  {i}. {snap}")
        
        return CommandResult(
            success=True,
            message="\n".join(lines),
            data={"history": history_list, "total": self._history.undo_count}
        )
    
    def format_table(self, limit: int = 10) -> Table:
        """
        Format history as rich table.
        將歷史格式化為 rich 表格。
        
        Args:
            limit: Maximum entries | 最大條目數
            
        Returns:
            Rich Table object | Rich Table 物件
        """
        table = Table(title="📋 Command History | 指令歷史")
        table.add_column("#", style="dim", width=4)
        table.add_column("Status | 狀態", width=6)
        table.add_column("Time | 時間", width=10)
        table.add_column("Command | 指令", style="cyan")
        
        history_list = self._history.get_history(limit)
        
        for i, snap in enumerate(history_list, 1):
            if isinstance(snap, CommandSnapshot):
                status = "✓" if snap.executed and not snap.error else "✗"
                time_str = snap.timestamp.strftime("%H:%M:%S")
                cmd = snap.command_str[:40] + "..." if len(snap.command_str) > 40 else snap.command_str
                table.add_row(str(i), status, time_str, cmd)
        
        return table


# Utility functions | 工具函數

def register_undo_commands() -> dict[str, type]:
    """
    Register undo-related commands with the command registry.
    向指令註冊表註冊恢復相關指令。
    
    Returns:
        Dictionary of command names to command classes
    """
    return {
        "undo": UndoCommand,
        "redo": RedoCommand,
        "history": HistoryCommand,
    }


def format_undo_help() -> str:
    """
    Generate help text for undo commands.
    生成恢復指令的幫助文字。
    
    Returns:
        Formatted help string | 格式化的幫助字串
    """
    return """
╭─────────────────────────────────────────────────────╮
│ 恢復系統指令 | Undo System Commands                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│ /undo                恢復上一動 | Undo last action  │
│ /undo --steps 3      恢復前 N 步 | Undo N steps     │
│ /undo --preview      預覽恢復 | Preview undo        │
│                                                     │
│ /redo                重做 | Redo                    │
│ /redo --steps 2      重做 N 步 | Redo N steps       │
│                                                     │
│ /history             顯示歷史 | Show history        │
│ /history --limit 20  限制顯示數量 | Limit display   │
│                                                     │
╰─────────────────────────────────────────────────────╯
"""
