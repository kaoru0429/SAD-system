"""
Tests for SABE-Hacks Integration | SABE-Hacks 整合測試
"""

import pytest
from pathlib import Path
import tempfile

from src.integration import (
    SABEHacksIntegration,
    IntegrationConfig,
    create_integration,
)
from src.sabe.protocol import SABEProtocol, SABEMode
from src.progress_hacks import ProgressTracker, HackInjector, load_hacks
from src.undo import HistoryStack, reset_history
from src.core.parser import CommandParser


@pytest.fixture(autouse=True)
def fresh_history():
    """Reset global history before each test."""
    reset_history()
    yield
    reset_history()


class TestIntegrationConfig:
    """Test IntegrationConfig class."""
    
    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = IntegrationConfig()
        
        assert config.auto_suggest_clarify_on_ambiguous
        assert config.enforce_devil_on_high_risk
        assert config.recommend_all_hacks_on_large_task
        assert config.record_to_history
        assert config.show_progress_indicator


class TestSABEHacksIntegration:
    """Test SABEHacksIntegration class."""
    
    @pytest.fixture
    def integration(self) -> SABEHacksIntegration:
        """Create integration instance."""
        return SABEHacksIntegration()
    
    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create command parser."""
        return CommandParser()
    
    def test_create_integration(self, integration: SABEHacksIntegration) -> None:
        """Test creating integration."""
        assert integration is not None
    
    def test_get_status(self, integration: SABEHacksIntegration) -> None:
        """Test getting status."""
        status = integration.get_status()
        
        assert "progress" in status
        assert "history" in status
        assert "hacks" in status
    
    def test_format_status_display(self, integration: SABEHacksIntegration) -> None:
        """Test formatting status display."""
        display = integration.format_status_display()
        
        assert "SAD System v1.0" in display
        assert "History" in display
    
    def test_set_total_steps(self, integration: SABEHacksIntegration) -> None:
        """Test setting total steps."""
        integration.set_total_steps(100)
        
        status = integration.get_status()
        assert status["progress"]["current"] == 0
    
    def test_reset_progress(self, integration: SABEHacksIntegration) -> None:
        """Test resetting progress."""
        integration.set_total_steps(100)
        integration.reset_progress()
        
        status = integration.get_status()
        assert status["progress"]["current"] == 0


class TestHacksForMode:
    """Test hack recommendations for SABE modes."""
    
    @pytest.fixture
    def integration(self) -> SABEHacksIntegration:
        """Create integration instance."""
        return SABEHacksIntegration()
    
    def test_ambiguous_suggests_clarify(self, integration: SABEHacksIntegration) -> None:
        """Test that ambiguous mode suggests clarify hack."""
        hacks = integration._get_hacks_for_mode(SABEMode.AMBIGUOUS_REPAIR)
        
        hack_ids = [h.id for h in hacks]
        assert "clarify" in hack_ids
    
    def test_high_risk_enforces_devil(self, integration: SABEHacksIntegration) -> None:
        """Test that high risk mode enforces devil's advocate."""
        hacks = integration._get_hacks_for_mode(SABEMode.HIGH_RISK_CONFIRM)
        
        hack_ids = [h.id for h in hacks]
        assert "devils_advocate" in hack_ids
    
    def test_large_task_recommends_all(self, integration: SABEHacksIntegration) -> None:
        """Test that large task mode recommends all hacks."""
        hacks = integration._get_hacks_for_mode(SABEMode.LARGE_TASK_CONFIRM)
        
        hack_ids = [h.id for h in hacks]
        assert len(hack_ids) >= 3  # At least clarify, web, self-grade
    
    def test_input_missing_suggests_clarify(self, integration: SABEHacksIntegration) -> None:
        """Test that input missing suggests clarify."""
        hacks = integration._get_hacks_for_mode(SABEMode.INPUT_MISSING)
        
        hack_ids = [h.id for h in hacks]
        assert "clarify" in hack_ids


class TestCheckAndEnhance:
    """Test check_and_enhance method."""
    
    @pytest.fixture
    def integration(self) -> SABEHacksIntegration:
        """Create integration instance."""
        return SABEHacksIntegration()
    
    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create command parser."""
        return CommandParser()
    
    def test_high_risk_command_enhances(
        self, 
        integration: SABEHacksIntegration, 
        parser: CommandParser
    ) -> None:
        """Test that high risk command gets enhanced with devil's advocate."""
        command = parser.parse("/delete-file @file:important.txt")
        prompt = "Delete this file please"
        
        sabe_response, enhanced_prompt, applied_hacks = integration.check_and_enhance(
            command, prompt
        )
        
        assert sabe_response.triggered
        assert sabe_response.mode == SABEMode.HIGH_RISK_CONFIRM
        assert len(applied_hacks) > 0
        assert any(h.id == "devils_advocate" for h in applied_hacks)
    
    def test_ambiguous_command_enhances(
        self, 
        integration: SABEHacksIntegration, 
        parser: CommandParser
    ) -> None:
        """Test that ambiguous command gets enhanced with clarify."""
        command = parser.parse("/figure-out @data:sales")
        prompt = "Figure this out"
        context = {
            "mapping_confidence": 45.0,
            "candidates": [
                {"command": "/analyze-data", "description": "分析", "confidence": 80},
            ]
        }
        
        sabe_response, enhanced_prompt, applied_hacks = integration.check_and_enhance(
            command, prompt, context
        )
        
        assert sabe_response.triggered
        assert sabe_response.mode == SABEMode.AMBIGUOUS_REPAIR
        if applied_hacks:
            assert any(h.id == "clarify" for h in applied_hacks)
    
    def test_safe_command_no_sabe(
        self, 
        integration: SABEHacksIntegration, 
        parser: CommandParser
    ) -> None:
        """Test that safe command doesn't trigger SABE."""
        command = parser.parse("/analyze-data @file:safe.csv")
        prompt = "Analyze this data"
        
        sabe_response, enhanced_prompt, applied_hacks = integration.check_and_enhance(
            command, prompt
        )
        
        assert not sabe_response.triggered
    
    def test_records_to_history(
        self, 
        integration: SABEHacksIntegration, 
        parser: CommandParser
    ) -> None:
        """Test that commands are recorded to history."""
        command = parser.parse("/analyze-data @file:test.csv")
        prompt = "Analyze"
        
        initial_count = integration._history.undo_count
        
        integration.check_and_enhance(command, prompt)
        
        assert integration._history.undo_count > initial_count


class TestProgressIntegration:
    """Test progress tracking integration."""
    
    @pytest.fixture
    def integration(self) -> SABEHacksIntegration:
        """Create integration instance."""
        return SABEHacksIntegration()
    
    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create command parser."""
        return CommandParser()
    
    def test_progress_milestone_triggers_hack(
        self, 
        integration: SABEHacksIntegration, 
        parser: CommandParser
    ) -> None:
        """Test that reaching a milestone triggers hack injection."""
        integration.set_total_steps(100)
        
        command = parser.parse("/analyze-data @file:test.csv")
        prompt = "Analyze data"
        context = {"progress": 25}  # Past 20% milestone
        
        sabe_response, enhanced_prompt, applied_hacks = integration.check_and_enhance(
            command, prompt, context
        )
        
        # Clarify hack should be injected at 20%
        if applied_hacks:
            assert any(h.milestone == 20 for h in applied_hacks)


class TestCreateIntegration:
    """Test factory function."""
    
    def test_create_with_defaults(self) -> None:
        """Test creating integration with defaults."""
        integration = create_integration(auto_setup=False)
        assert isinstance(integration, SABEHacksIntegration)
