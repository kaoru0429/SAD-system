"""
Tests for Undo Module | 恢復模組測試
"""

import pytest
from datetime import datetime

from src.undo.snapshots import (
    CommandSnapshot,
    StateSnapshot,
    CompositeSnapshot,
    SnapshotType,
    create_snapshot,
)
from src.undo.history import (
    HistoryStack,
    HistoryConfig,
    get_history,
    reset_history,
)
from src.undo.commands import (
    UndoCommand,
    RedoCommand,
    HistoryCommand,
    CommandResult,
)


class TestStateSnapshot:
    """Test StateSnapshot class."""
    
    def test_create_snapshot(self) -> None:
        """Test creating a state snapshot."""
        snapshot = StateSnapshot(
            key="test_key",
            before={"value": 1},
            after={"value": 2}
        )
        
        assert snapshot.key == "test_key"
        assert snapshot.before == {"value": 1}
        assert snapshot.after == {"value": 2}
        assert snapshot.can_restore()
    
    def test_restore_value(self) -> None:
        """Test getting restore value."""
        snapshot = StateSnapshot(key="k", before="old", after="new")
        assert snapshot.restore_value() == "old"
        assert snapshot.redo_value() == "new"
    
    def test_cannot_restore_none(self) -> None:
        """Test snapshot with None before value."""
        snapshot = StateSnapshot(key="k", before=None, after="new")
        assert not snapshot.can_restore()


class TestCommandSnapshot:
    """Test CommandSnapshot class."""
    
    def test_create_command_snapshot(self) -> None:
        """Test creating a command snapshot."""
        snapshot = CommandSnapshot(
            id="cmd_001",
            command_str="/analyze-data @file:test.csv",
            command_name="analyze-data"
        )
        
        assert snapshot.id == "cmd_001"
        assert snapshot.command_name == "analyze-data"
        assert snapshot.reversible
        assert not snapshot.executed
    
    def test_add_state(self) -> None:
        """Test adding state to snapshot."""
        snapshot = CommandSnapshot(
            id="cmd_001",
            command_str="/test",
            command_name="test"
        )
        
        snapshot.add_state("key1", "old", "new")
        
        assert len(snapshot.states) == 1
        assert snapshot.states[0].key == "key1"
    
    def test_mark_executed(self) -> None:
        """Test marking as executed."""
        snapshot = CommandSnapshot(
            id="cmd_001",
            command_str="/test",
            command_name="test"
        )
        
        snapshot.mark_executed(result={"success": True})
        
        assert snapshot.executed
        assert snapshot.result == {"success": True}
        assert snapshot.can_undo()
    
    def test_mark_executed_with_error(self) -> None:
        """Test marking as executed with error."""
        snapshot = CommandSnapshot(
            id="cmd_001",
            command_str="/test",
            command_name="test"
        )
        
        snapshot.mark_executed(error="Something failed")
        
        assert snapshot.executed
        assert snapshot.error == "Something failed"
        assert not snapshot.can_undo()  # Cannot undo failed commands
    
    def test_display_str(self) -> None:
        """Test display string generation."""
        snapshot = CommandSnapshot(
            id="cmd_001",
            command_str="/analyze-data @file:test.csv",
            command_name="analyze-data"
        )
        snapshot.mark_executed()
        
        display = snapshot.get_display_str()
        assert "analyze-data" in display
        assert "✓" in display


class TestCompositeSnapshot:
    """Test CompositeSnapshot class."""
    
    def test_create_composite(self) -> None:
        """Test creating composite snapshot."""
        composite = CompositeSnapshot(
            id="batch_001",
            description="Batch operation"
        )
        
        snap1 = CommandSnapshot(id="1", command_str="/cmd1", command_name="cmd1")
        snap2 = CommandSnapshot(id="2", command_str="/cmd2", command_name="cmd2")
        
        composite.add_snapshot(snap1)
        composite.add_snapshot(snap2)
        
        assert composite.snapshot_count == 2


class TestHistoryStack:
    """Test HistoryStack class."""
    
    @pytest.fixture
    def history(self) -> HistoryStack:
        """Create fresh history stack."""
        return HistoryStack(HistoryConfig(max_history=10))
    
    def test_push_and_undo(self, history: HistoryStack) -> None:
        """Test push and undo operations."""
        snap = CommandSnapshot(id="1", command_str="/test", command_name="test")
        snap.mark_executed()
        
        history.push(snap)
        
        assert history.can_undo
        assert history.undo_count == 1
        
        undone = history.undo()
        
        assert undone == snap
        assert history.undo_count == 0
        assert history.can_redo
    
    def test_redo(self, history: HistoryStack) -> None:
        """Test redo operation."""
        snap = CommandSnapshot(id="1", command_str="/test", command_name="test")
        snap.mark_executed()
        
        history.push(snap)
        history.undo()
        
        redone = history.redo()
        
        assert redone == snap
        assert history.can_undo
        assert not history.can_redo
    
    def test_undo_steps(self, history: HistoryStack) -> None:
        """Test undoing multiple steps."""
        for i in range(5):
            snap = CommandSnapshot(id=str(i), command_str=f"/cmd{i}", command_name=f"cmd{i}")
            snap.mark_executed()
            history.push(snap)
        
        undone = history.undo_steps(3)
        
        assert len(undone) == 3
        assert history.undo_count == 2
        assert history.redo_count == 3
    
    def test_push_clears_redo(self, history: HistoryStack) -> None:
        """Test that push clears redo stack."""
        snap1 = CommandSnapshot(id="1", command_str="/cmd1", command_name="cmd1")
        snap1.mark_executed()
        history.push(snap1)
        history.undo()
        
        assert history.can_redo
        
        snap2 = CommandSnapshot(id="2", command_str="/cmd2", command_name="cmd2")
        snap2.mark_executed()
        history.push(snap2)
        
        assert not history.can_redo
    
    def test_max_history(self) -> None:
        """Test maximum history limit."""
        history = HistoryStack(HistoryConfig(max_history=3))
        
        for i in range(5):
            snap = CommandSnapshot(id=str(i), command_str=f"/cmd{i}", command_name=f"cmd{i}")
            history.push(snap)
        
        assert history.undo_count == 3
    
    def test_preview(self, history: HistoryStack) -> None:
        """Test preview functionality."""
        for i in range(3):
            snap = CommandSnapshot(id=str(i), command_str=f"/cmd{i}", command_name=f"cmd{i}")
            history.push(snap)
        
        preview = history.get_preview(2)
        
        assert len(preview) == 2
        assert history.undo_count == 3  # Preview doesn't remove


class TestUndoCommand:
    """Test UndoCommand class."""
    
    @pytest.fixture
    def history(self) -> HistoryStack:
        """Create history with some commands."""
        history = HistoryStack()
        for i in range(3):
            snap = CommandSnapshot(id=str(i), command_str=f"/cmd{i}", command_name=f"cmd{i}")
            snap.mark_executed()
            history.push(snap)
        return history
    
    def test_undo_success(self, history: HistoryStack) -> None:
        """Test successful undo."""
        cmd = UndoCommand(history)
        result = cmd.execute(steps=1)
        
        assert result.success
        assert "1" in result.message or "已恢復" in result.message
    
    def test_undo_preview(self, history: HistoryStack) -> None:
        """Test undo preview."""
        cmd = UndoCommand(history)
        result = cmd.execute(preview=True)
        
        assert result.success
        assert result.data["preview"]
        assert history.undo_count == 3  # Not actually undone
    
    def test_undo_empty(self) -> None:
        """Test undo on empty history."""
        fresh_history = HistoryStack()
        cmd = UndoCommand(fresh_history)
        result = cmd.execute()
        
        assert not result.success


class TestRedoCommand:
    """Test RedoCommand class."""
    
    def test_redo_success(self) -> None:
        """Test successful redo."""
        history = HistoryStack()
        snap = CommandSnapshot(id="1", command_str="/test", command_name="test")
        snap.mark_executed()
        history.push(snap)
        history.undo()
        
        cmd = RedoCommand(history)
        result = cmd.execute()
        
        assert result.success
    
    def test_redo_empty(self) -> None:
        """Test redo with nothing to redo."""
        fresh_history = HistoryStack()
        cmd = RedoCommand(fresh_history)
        result = cmd.execute()
        
        assert not result.success


class TestHistoryCommand:
    """Test HistoryCommand class."""
    
    def test_show_history(self) -> None:
        """Test showing history."""
        history = HistoryStack()
        for i in range(5):
            snap = CommandSnapshot(id=str(i), command_str=f"/cmd{i}", command_name=f"cmd{i}")
            snap.mark_executed()
            history.push(snap)
        
        cmd = HistoryCommand(history)
        result = cmd.execute(limit=3)
        
        assert result.success
        assert len(result.data["history"]) == 3
    
    def test_empty_history(self) -> None:
        """Test empty history message."""
        fresh_history = HistoryStack()
        cmd = HistoryCommand(fresh_history)
        result = cmd.execute()
        
        assert result.success
        assert "empty" in result.message.lower() or "空" in result.message
