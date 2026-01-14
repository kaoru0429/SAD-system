"""
Snapshots - 狀態快照

Manages state snapshots for undo/redo operations.
管理用於恢復/重做操作的狀態快照。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from enum import Enum


class SnapshotType(Enum):
    """快照類型 | Snapshot Type"""
    COMMAND = "command"      # 指令執行 | Command execution
    STATE = "state"          # 狀態變更 | State change
    FILE = "file"            # 檔案操作 | File operation
    COMPOSITE = "composite"  # 複合操作 | Composite operation


@dataclass
class StateSnapshot:
    """
    狀態快照 | State Snapshot
    
    Captures the state before and after an operation.
    擷取操作前後的狀態。
    
    Example:
        >>> snapshot = StateSnapshot(
        ...     key="current_file",
        ...     before={"name": "old.txt"},
        ...     after={"name": "new.txt"}
        ... )
    """
    key: str
    before: Any
    after: Any
    timestamp: datetime = field(default_factory=datetime.now)
    
    def can_restore(self) -> bool:
        """
        Check if this snapshot can be restored.
        檢查此快照是否可恢復。
        """
        return self.before is not None
    
    def restore_value(self) -> Any:
        """
        Get the value to restore to.
        取得要恢復的值。
        """
        return self.before
    
    def redo_value(self) -> Any:
        """
        Get the value for redo.
        取得重做的值。
        """
        return self.after


@dataclass
class CommandSnapshot:
    """
    指令快照 | Command Snapshot
    
    Captures a complete command execution context for undo/redo.
    擷取完整的指令執行上下文以供恢復/重做。
    
    Attributes:
        id: Unique identifier | 唯一識別符
        command_str: Original command string | 原始指令字串
        command_name: Parsed command name | 解析後的指令名稱
        timestamp: Execution time | 執行時間
        states: State changes | 狀態變更列表
        reversible: Whether can be undone | 是否可恢復
        executed: Whether executed successfully | 是否成功執行
        result: Execution result | 執行結果
        
    Example:
        >>> snapshot = CommandSnapshot(
        ...     id="cmd_001",
        ...     command_str="/analyze-data @file:sales.csv",
        ...     command_name="analyze-data"
        ... )
    """
    id: str
    command_str: str
    command_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    snapshot_type: SnapshotType = SnapshotType.COMMAND
    states: list[StateSnapshot] = field(default_factory=list)
    reversible: bool = True
    executed: bool = False
    result: Any = None
    error: str | None = None
    
    def add_state(self, key: str, before: Any, after: Any) -> None:
        """
        Add a state change to this snapshot.
        新增狀態變更到此快照。
        
        Args:
            key: State identifier | 狀態識別符
            before: Value before operation | 操作前的值
            after: Value after operation | 操作後的值
        """
        self.states.append(StateSnapshot(key=key, before=before, after=after))
    
    def mark_executed(self, result: Any = None, error: str | None = None) -> None:
        """
        Mark this command as executed.
        標記此指令已執行。
        
        Args:
            result: Execution result | 執行結果
            error: Error message if failed | 錯誤訊息（如果失敗）
        """
        self.executed = True
        self.result = result
        self.error = error
        if error:
            self.reversible = False
    
    def can_undo(self) -> bool:
        """
        Check if this command can be undone.
        檢查此指令是否可恢復。
        
        Returns:
            True if reversible and executed | 如果可恢復且已執行則返回 True
        """
        return self.reversible and self.executed and not self.error
    
    def get_display_str(self, max_length: int = 50) -> str:
        """
        Get display string for history view.
        取得歷史檢視的顯示字串。
        
        Args:
            max_length: Maximum display length | 最大顯示長度
            
        Returns:
            Formatted display string | 格式化的顯示字串
        """
        cmd = self.command_str
        if len(cmd) > max_length:
            cmd = cmd[:max_length - 3] + "..."
        
        status = "✓" if self.executed and not self.error else "✗" if self.error else "○"
        time_str = self.timestamp.strftime("%H:%M:%S")
        
        return f"{status} [{time_str}] {cmd}"
    
    def __str__(self) -> str:
        return self.get_display_str()


@dataclass  
class CompositeSnapshot:
    """
    複合快照 | Composite Snapshot
    
    Groups multiple command snapshots for atomic undo/redo.
    將多個指令快照分組以進行原子性恢復/重做。
    
    Example:
        >>> composite = CompositeSnapshot(
        ...     id="batch_001",
        ...     description="Batch file processing"
        ... )
        >>> composite.add_snapshot(snapshot1)
        >>> composite.add_snapshot(snapshot2)
    """
    id: str
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    snapshots: list[CommandSnapshot] = field(default_factory=list)
    
    def add_snapshot(self, snapshot: CommandSnapshot) -> None:
        """Add a snapshot to this composite."""
        self.snapshots.append(snapshot)
    
    def can_undo(self) -> bool:
        """Check if all snapshots can be undone."""
        return all(s.can_undo() for s in self.snapshots)
    
    @property
    def snapshot_count(self) -> int:
        """Get number of snapshots."""
        return len(self.snapshots)


# Type alias for any snapshot type
AnySnapshot = CommandSnapshot | CompositeSnapshot


def create_snapshot(
    command_str: str,
    command_name: str,
    snapshot_id: str | None = None
) -> CommandSnapshot:
    """
    Factory function to create a command snapshot.
    建立指令快照的工廠函數。
    
    Args:
        command_str: Original command string | 原始指令字串
        command_name: Parsed command name | 解析後的指令名稱
        snapshot_id: Optional custom ID | 可選的自訂 ID
        
    Returns:
        New CommandSnapshot instance | 新的 CommandSnapshot 實例
    """
    import uuid
    
    return CommandSnapshot(
        id=snapshot_id or f"snap_{uuid.uuid4().hex[:8]}",
        command_str=command_str,
        command_name=command_name
    )
