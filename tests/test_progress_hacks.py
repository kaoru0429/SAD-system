"""
Tests for Progress Hacks Module | 五言絕句模組測試
"""

import pytest

from src.progress_hacks.hacks import (
    PromptHack,
    load_hacks,
    get_hack_by_id,
    get_hack_by_milestone,
    get_enabled_hacks,
    DEFAULT_HACKS,
)
from src.progress_hacks.tracker import (
    ProgressTracker,
    Milestone,
    MilestoneStatus,
    ProgressState,
)
from src.progress_hacks.injector import (
    HackInjector,
    InjectionStyle,
    InjectionPosition,
    create_injector,
)


class TestPromptHack:
    """Test PromptHack class."""
    
    def test_create_hack(self) -> None:
        """Test creating a prompt hack."""
        hack = PromptHack(
            id="test",
            name_zh="測試",
            name_en="Test",
            emoji="🧪",
            milestone=50,
            postscript="Test postscript"
        )
        
        assert hack.id == "test"
        assert hack.milestone == 50
        assert hack.enabled
    
    def test_display_name(self) -> None:
        """Test display name formatting."""
        hack = PromptHack(
            id="clarify",
            name_zh="先澄清",
            name_en="Clarify",
            emoji="🎯",
            milestone=20,
            postscript="test"
        )
        
        assert "🎯" in hack.display_name
        assert "Clarify" in hack.display_name
        assert "先澄清" in hack.display_name
    
    def test_get_postscript(self) -> None:
        """Test getting postscript."""
        hack = PromptHack(
            id="test",
            name_zh="測試",
            name_en="Test",
            emoji="🧪",
            milestone=50,
            postscript="Main postscript",
            enhanced="Enhanced version"
        )
        
        assert hack.get_postscript() == "Main postscript"
        assert "Enhanced" in hack.get_postscript(enhanced=True)
    
    def test_format_injection(self) -> None:
        """Test injection formatting."""
        hack = PromptHack(
            id="test",
            name_zh="測試",
            name_en="Test",
            emoji="🧪",
            milestone=50,
            postscript="Test postscript"
        )
        
        minimal = hack.format_injection(style="minimal")
        assert minimal == "Test postscript"


class TestLoadHacks:
    """Test hack loading functions."""
    
    def test_load_defaults(self) -> None:
        """Test loading default hacks."""
        hacks = load_hacks()
        
        assert len(hacks) == 5
        assert hacks[0].milestone == 20
        assert hacks[-1].milestone == 100
    
    def test_get_by_id(self) -> None:
        """Test getting hack by ID."""
        hacks = load_hacks()
        
        clarify = get_hack_by_id(hacks, "clarify")
        assert clarify is not None
        assert clarify.name_en == "Clarify"
        
        missing = get_hack_by_id(hacks, "nonexistent")
        assert missing is None
    
    def test_get_by_milestone(self) -> None:
        """Test getting hack by milestone."""
        hacks = load_hacks()
        
        hack_20 = get_hack_by_milestone(hacks, 20)
        assert hack_20 is not None
        assert hack_20.id == "clarify"
    
    def test_get_enabled(self) -> None:
        """Test getting only enabled hacks."""
        hacks = load_hacks()
        enabled = get_enabled_hacks(hacks)
        
        # Default has expert_panel disabled
        assert len(enabled) == 4
        assert all(h.enabled for h in enabled)


class TestMilestone:
    """Test Milestone class."""
    
    def test_create_milestone(self) -> None:
        """Test creating a milestone."""
        hack = PromptHack(
            id="test", name_zh="測試", name_en="Test",
            emoji="🧪", milestone=50, postscript="test"
        )
        milestone = Milestone(percentage=50, hack=hack)
        
        assert milestone.percentage == 50
        assert milestone.status == MilestoneStatus.PENDING
        assert milestone.indicator == "○"
    
    def test_mark_reached(self) -> None:
        """Test marking milestone as reached."""
        milestone = Milestone(percentage=50, hack=None)
        milestone.mark_reached()
        
        assert milestone.status == MilestoneStatus.REACHED
        assert milestone.reached_at is not None
    
    def test_mark_injected(self) -> None:
        """Test marking milestone as injected."""
        milestone = Milestone(percentage=50, hack=None)
        milestone.mark_injected()
        
        assert milestone.status == MilestoneStatus.INJECTED
        assert milestone.indicator == "●"


class TestProgressTracker:
    """Test ProgressTracker class."""
    
    @pytest.fixture
    def tracker(self) -> ProgressTracker:
        """Create a progress tracker."""
        return ProgressTracker()
    
    def test_initial_state(self, tracker: ProgressTracker) -> None:
        """Test initial tracker state."""
        assert tracker.current_percentage == 0.0
        assert not tracker.is_complete
        assert tracker.get_remaining_count() == 5
    
    def test_set_total(self, tracker: ProgressTracker) -> None:
        """Test setting total progress."""
        tracker.set_total(200)
        tracker.update_progress(100)
        
        assert tracker.current_percentage == 50.0
    
    def test_milestone_trigger(self, tracker: ProgressTracker) -> None:
        """Test milestone triggering."""
        tracker.set_total(100)
        
        # No trigger at 10%
        hack = tracker.update_progress(10)
        assert hack is None
        
        # Trigger at 20%
        hack = tracker.update_progress(20)
        assert hack is not None
        assert hack.id == "clarify"
    
    def test_increment_progress(self, tracker: ProgressTracker) -> None:
        """Test incremental progress."""
        tracker.set_total(100)
        
        for i in range(25):
            hack = tracker.increment_progress(1)
        
        assert tracker.current_percentage == 25.0
    
    def test_no_double_trigger(self, tracker: ProgressTracker) -> None:
        """Test milestone doesn't trigger twice."""
        tracker.set_total(100)
        
        hack1 = tracker.update_progress(25)  # First trigger at 20%
        assert hack1 is not None
        
        hack2 = tracker.update_progress(30)  # Should not trigger 20% again
        assert hack2 is None
    
    def test_progress_indicator(self, tracker: ProgressTracker) -> None:
        """Test progress indicator generation."""
        tracker.set_total(100)
        tracker.update_progress(50)
        
        indicator = tracker.get_progress_indicator()
        
        assert "●" in indicator or "○" in indicator
        assert "50%" in indicator or "50" in indicator
    
    def test_compact_indicator(self, tracker: ProgressTracker) -> None:
        """Test compact indicator."""
        tracker.set_total(100)
        tracker.update_progress(25)
        
        compact = tracker.get_compact_indicator()
        
        assert "25" in compact
        assert "🎯" in compact
    
    def test_reset(self, tracker: ProgressTracker) -> None:
        """Test tracker reset."""
        tracker.set_total(100)
        tracker.update_progress(50)
        tracker.reset()
        
        assert tracker.current_percentage == 0.0
        assert tracker.get_remaining_count() == 5


class TestHackInjector:
    """Test HackInjector class."""
    
    @pytest.fixture
    def injector(self) -> HackInjector:
        """Create a hack injector."""
        return HackInjector()
    
    @pytest.fixture
    def sample_hack(self) -> PromptHack:
        """Create a sample hack."""
        return PromptHack(
            id="test",
            name_zh="測試",
            name_en="Test",
            emoji="🧪",
            milestone=50,
            postscript="This is the test postscript."
        )
    
    def test_inject_append(self, injector: HackInjector, sample_hack: PromptHack) -> None:
        """Test appending injection."""
        result = injector.inject(
            prompt="Original prompt",
            hack=sample_hack,
            position=InjectionPosition.APPEND
        )
        
        assert result.was_modified
        assert result.injected_prompt.startswith("Original prompt")
        assert "test postscript" in result.injected_prompt.lower()
    
    def test_inject_prepend(self, injector: HackInjector, sample_hack: PromptHack) -> None:
        """Test prepending injection."""
        result = injector.inject(
            prompt="Original prompt",
            hack=sample_hack,
            position=InjectionPosition.PREPEND
        )
        
        assert result.was_modified
        assert "Original prompt" in result.injected_prompt
        assert result.injected_prompt.find("test") < result.injected_prompt.find("Original")
    
    def test_inject_minimal_style(self, injector: HackInjector, sample_hack: PromptHack) -> None:
        """Test minimal style injection."""
        result = injector.inject(
            prompt="Original",
            hack=sample_hack,
            style=InjectionStyle.MINIMAL
        )
        
        # Minimal should just have the postscript
        assert "This is the test postscript" in result.injected_prompt
    
    def test_inject_boxed_style(self, injector: HackInjector, sample_hack: PromptHack) -> None:
        """Test boxed style injection."""
        result = injector.inject(
            prompt="Original",
            hack=sample_hack,
            style=InjectionStyle.BOXED
        )
        
        # Should have box characters
        assert "╭" in result.injected_prompt or "─" in result.injected_prompt
    
    def test_format_notification(self, injector: HackInjector, sample_hack: PromptHack) -> None:
        """Test notification formatting."""
        notification = injector.format_notification(sample_hack)
        
        assert "✨" in notification
        assert "Test" in notification
    
    def test_format_preview(self, injector: HackInjector, sample_hack: PromptHack) -> None:
        """Test preview formatting."""
        preview = injector.format_preview(sample_hack)
        
        assert "Postscript" in preview or "附言" in preview


class TestCreateInjector:
    """Test factory function."""
    
    def test_create_with_defaults(self) -> None:
        """Test creating with defaults."""
        injector = create_injector()
        assert isinstance(injector, HackInjector)
    
    def test_create_with_options(self) -> None:
        """Test creating with options."""
        injector = create_injector(style="boxed", position="prepend")
        assert isinstance(injector, HackInjector)
