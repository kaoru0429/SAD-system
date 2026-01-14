"""
Tests for Setup Module | 設定模組測試
"""

import pytest
from pathlib import Path
import tempfile
import json

from src.progress_hacks.setup.presets import (
    Preset,
    PresetType,
    get_presets,
    get_preset_by_id,
    get_recommended_preset,
    DEFAULT_PRESETS,
)
from src.progress_hacks.setup.wizard import (
    SetupWizard,
    SetupConfig,
    SetupState,
)


class TestPreset:
    """Test Preset class."""
    
    def test_create_preset(self) -> None:
        """Test creating a preset."""
        preset = Preset(
            id="test",
            name_zh="測試",
            name_en="Test",
            description_zh="測試描述",
            description_en="Test description",
            enabled_hacks=["clarify", "self_grade"]
        )
        
        assert preset.id == "test"
        assert len(preset.enabled_hacks) == 2
    
    def test_display_name(self) -> None:
        """Test display name formatting."""
        preset = Preset(
            id="test",
            name_zh="測試",
            name_en="Test",
            description_zh="",
            description_en="",
            enabled_hacks=[],
            icon="🧪"
        )
        
        assert "🧪" in preset.display_name
        assert "Test" in preset.display_name
        assert "測試" in preset.display_name
    
    def test_get_enabled_emojis(self) -> None:
        """Test emoji representation."""
        preset = Preset(
            id="test",
            name_zh="測試",
            name_en="Test",
            description_zh="",
            description_en="",
            enabled_hacks=["clarify", "web_backed"]
        )
        
        emojis = preset.get_enabled_emojis()
        assert "🎯" in emojis
        assert "🌐" in emojis


class TestGetPresets:
    """Test preset retrieval functions."""
    
    def test_get_all_presets(self) -> None:
        """Test getting all presets."""
        presets = get_presets()
        
        assert len(presets) == 7
        assert presets[0].id == "recommended"
    
    def test_get_by_id(self) -> None:
        """Test getting preset by ID."""
        preset = get_preset_by_id("recommended")
        
        assert preset is not None
        assert preset.id == "recommended"
        assert "clarify" in preset.enabled_hacks
    
    def test_get_by_id_not_found(self) -> None:
        """Test getting nonexistent preset."""
        preset = get_preset_by_id("nonexistent")
        assert preset is None
    
    def test_get_recommended(self) -> None:
        """Test getting recommended preset."""
        preset = get_recommended_preset()
        
        assert preset.id == "recommended"
        # Recommended should not include expert_panel (too slow)
        assert "expert_panel" not in preset.enabled_hacks
        assert "clarify" in preset.enabled_hacks


class TestSetupConfig:
    """Test SetupConfig class."""
    
    def test_create_config(self) -> None:
        """Test creating config."""
        config = SetupConfig(
            enabled_hacks=["clarify", "self_grade"],
            preset_used="custom"
        )
        
        assert len(config.enabled_hacks) == 2
        assert not config.setup_completed
    
    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        config = SetupConfig(
            enabled_hacks=["clarify"],
            setup_completed=True
        )
        
        data = config.to_dict()
        
        assert "enabled_hacks" in data
        assert data["setup_completed"] is True
    
    def test_from_dict(self) -> None:
        """Test creating from dictionary."""
        data = {
            "enabled_hacks": ["clarify", "web_backed"],
            "preset_used": "recommended",
            "setup_completed": True,
            "show_progress_indicator": True,
            "auto_inject": True,
            "notify_on_inject": True,
        }
        
        config = SetupConfig.from_dict(data)
        
        assert config.enabled_hacks == ["clarify", "web_backed"]
        assert config.setup_completed
    
    def test_save_and_load(self) -> None:
        """Test saving and loading config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            
            config = SetupConfig(
                enabled_hacks=["clarify", "self_grade"],
                setup_completed=True
            )
            config.save(path)
            
            loaded = SetupConfig.load(path)
            
            assert loaded is not None
            assert loaded.enabled_hacks == ["clarify", "self_grade"]
            assert loaded.setup_completed
    
    def test_load_nonexistent(self) -> None:
        """Test loading nonexistent file."""
        path = Path("/nonexistent/path/config.json")
        loaded = SetupConfig.load(path)
        assert loaded is None


class TestSetupWizard:
    """Test SetupWizard class."""
    
    @pytest.fixture
    def wizard(self) -> SetupWizard:
        """Create wizard with temp config path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield SetupWizard(config_path=Path(tmpdir) / "config.json")
    
    def test_initial_state(self, wizard: SetupWizard) -> None:
        """Test initial wizard state."""
        assert wizard.state == SetupState.NOT_STARTED
        assert wizard.is_first_run()
    
    def test_get_welcome_message(self, wizard: SetupWizard) -> None:
        """Test welcome message."""
        message = wizard.get_welcome_message()
        
        assert "Welcome" in message
        assert "歡迎" in message
        assert "Five Hacks" in message or "五言絕句" in message
        assert wizard.state == SetupState.WELCOME
    
    def test_get_preset_menu(self, wizard: SetupWizard) -> None:
        """Test preset menu."""
        menu = wizard.get_preset_menu()
        
        assert "Recommended" in menu or "推薦" in menu
        assert "[1]" in menu
    
    def test_get_custom_menu(self, wizard: SetupWizard) -> None:
        """Test custom menu."""
        wizard._config.enabled_hacks = ["clarify"]
        menu = wizard.get_custom_menu()
        
        assert "✓" in menu  # One enabled
        assert "○" in menu  # Others disabled
    
    def test_process_welcome_y(self, wizard: SetupWizard) -> None:
        """Test selecting Y (recommended)."""
        wizard.get_welcome_message()
        response, complete = wizard.process_input("Y")
        
        assert complete
        assert "Setup Complete" in response or "設定完成" in response
        assert wizard.config.preset_used == "recommended"
    
    def test_process_welcome_a(self, wizard: SetupWizard) -> None:
        """Test selecting A (all)."""
        wizard.get_welcome_message()
        response, complete = wizard.process_input("A")
        
        assert complete
        assert wizard.config.preset_used == "all"
        assert "expert_panel" in wizard.config.enabled_hacks
    
    def test_process_welcome_s(self, wizard: SetupWizard) -> None:
        """Test selecting S (skip)."""
        wizard.get_welcome_message()
        response, complete = wizard.process_input("S")
        
        assert complete
        assert len(wizard.config.enabled_hacks) == 0
    
    def test_process_welcome_c(self, wizard: SetupWizard) -> None:
        """Test selecting C (custom)."""
        wizard.get_welcome_message()
        response, complete = wizard.process_input("C")
        
        assert not complete
        assert wizard.state == SetupState.CUSTOM_CONFIG
    
    def test_process_custom_toggle(self, wizard: SetupWizard) -> None:
        """Test toggling hacks in custom mode."""
        wizard.get_welcome_message()
        wizard.process_input("C")
        
        initial_count = len(wizard.config.enabled_hacks)
        
        # Toggle first hack
        wizard.process_input("1")
        
        # Should have changed
        assert len(wizard.config.enabled_hacks) != initial_count or \
               "clarify" not in wizard.config.enabled_hacks
    
    def test_process_custom_done(self, wizard: SetupWizard) -> None:
        """Test completing custom config."""
        wizard.get_welcome_message()
        wizard.process_input("C")
        response, complete = wizard.process_input("D")
        
        assert complete
        assert wizard.config.preset_used == "custom"
    
    def test_invalid_input_welcome(self, wizard: SetupWizard) -> None:
        """Test invalid input at welcome screen."""
        wizard.get_welcome_message()
        response, complete = wizard.process_input("X")
        
        assert not complete
        assert "Invalid" in response or "❌" in response
    
    def test_config_persistence(self) -> None:
        """Test that config is saved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            
            wizard = SetupWizard(config_path=path)
            wizard.get_welcome_message()
            wizard.process_input("Y")
            
            # Config should be saved
            assert path.exists()
            
            # New wizard should see existing config
            wizard2 = SetupWizard(config_path=path)
            assert not wizard2.is_first_run()


class TestSetupFlow:
    """Test complete setup flows."""
    
    def test_full_recommended_flow(self) -> None:
        """Test complete recommended flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(config_path=Path(tmpdir) / "config.json")
            
            # Step 1: Welcome
            assert wizard.is_first_run()
            welcome = wizard.get_welcome_message()
            assert "Welcome" in welcome
            
            # Step 2: Select recommended
            response, complete = wizard.process_input("Y")
            
            # Verify
            assert complete
            assert wizard.config.setup_completed
            assert "clarify" in wizard.config.enabled_hacks
            assert "expert_panel" not in wizard.config.enabled_hacks
    
    def test_full_custom_flow(self) -> None:
        """Test complete custom flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(config_path=Path(tmpdir) / "config.json")
            
            # Step 1: Welcome
            wizard.get_welcome_message()
            
            # Step 2: Go to custom
            wizard.process_input("C")
            
            # Step 3: Toggle some hacks
            wizard.process_input("4")  # Toggle expert_panel
            
            # Step 4: Complete
            response, complete = wizard.process_input("D")
            
            assert complete
            assert wizard.config.preset_used == "custom"
