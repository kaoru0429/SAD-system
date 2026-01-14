"""
Setup Wizard - 設定精靈

Interactive first-run setup wizard for Five Hacks configuration.
五言絕句配置的互動式首次執行設定精靈。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any
from pathlib import Path
import json

from .presets import Preset, get_presets, get_preset_by_id, get_recommended_preset


class SetupState(Enum):
    """Setup wizard state | 設定精靈狀態"""
    NOT_STARTED = "not_started"
    WELCOME = "welcome"
    PRESET_SELECTION = "preset_selection"
    CUSTOM_CONFIG = "custom_config"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"


@dataclass
class SetupConfig:
    """
    Setup configuration result | 設定配置結果
    
    Stores the user's Five Hacks preferences.
    儲存用戶的五言絕句偏好。
    """
    enabled_hacks: list[str] = field(default_factory=list)
    preset_used: str | None = None
    setup_completed: bool = False
    show_progress_indicator: bool = True
    auto_inject: bool = True
    notify_on_inject: bool = True
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enabled_hacks": self.enabled_hacks,
            "preset_used": self.preset_used,
            "setup_completed": self.setup_completed,
            "show_progress_indicator": self.show_progress_indicator,
            "auto_inject": self.auto_inject,
            "notify_on_inject": self.notify_on_inject,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SetupConfig:
        """Create from dictionary."""
        return cls(**data)
    
    def save(self, path: Path) -> None:
        """Save config to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> SetupConfig | None:
        """Load config from file."""
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


class SetupWizard:
    """
    設定精靈 | Setup Wizard
    
    Interactive wizard for first-run configuration of Five Hacks.
    五言絕句首次執行配置的互動式精靈。
    
    Example:
        >>> wizard = SetupWizard()
        >>> print(wizard.get_welcome_message())
        >>> config = wizard.apply_preset("recommended")
    """
    
    HACK_INFO = {
        "clarify": {
            "emoji": "🎯",
            "name_zh": "先澄清",
            "name_en": "Clarify",
            "milestone": "20%",
        },
        "web_backed": {
            "emoji": "🌐",
            "name_zh": "網路查證",
            "name_en": "Web-backed",
            "milestone": "40%",
        },
        "self_grade": {
            "emoji": "📊",
            "name_zh": "自我評分",
            "name_en": "Self-grade",
            "milestone": "60%",
        },
        "expert_panel": {
            "emoji": "👥",
            "name_zh": "三專家觀點",
            "name_en": "3-Expert",
            "milestone": "80%",
        },
        "devils_advocate": {
            "emoji": "😈",
            "name_zh": "自我批判",
            "name_en": "Devil's Advocate",
            "milestone": "100%",
        },
    }
    
    def __init__(
        self,
        config_path: Path | None = None,
        on_complete: Callable[[SetupConfig], None] | None = None
    ) -> None:
        """
        Initialize setup wizard.
        初始化設定精靈。
        
        Args:
            config_path: Path to save config | 配置儲存路徑
            on_complete: Callback on completion | 完成時的回調
        """
        self._config_path = config_path or Path.home() / ".sad" / "config.json"
        self._on_complete = on_complete
        self._state = SetupState.NOT_STARTED
        self._config = SetupConfig()
        self._presets = get_presets()
    
    def is_first_run(self) -> bool:
        """
        Check if this is first run.
        檢查是否首次執行。
        """
        existing = SetupConfig.load(self._config_path)
        return existing is None or not existing.setup_completed
    
    def get_welcome_message(self) -> str:
        """
        Get the welcome message for first run.
        取得首次執行的歡迎訊息。
        """
        self._state = SetupState.WELCOME
        
        return """
╭─────────────────────────────────────────────────────────╮
│                                                         │
│  🎉 Welcome to SAD System! | 歡迎使用 SAD 系統！         │
│                                                         │
╰─────────────────────────────────────────────────────────╯

I noticed this is your first time. Let me help you get started.
我發現這是您第一次使用，讓我幫您快速設定。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Five Hacks automatically improve your prompts at key milestones:
五言絕句會在關鍵進度點自動提升您的 prompt：

  🎯 20%  - Ask clarifying questions first | 先澄清
  🌐 40%  - Search for latest info | 搜尋最新資訊
  📊 60%  - Self-evaluate to 9/10 | 自評迭代
  👥 80%  - Multi-expert perspectives | 多專家觀點
  😈 100% - Find blind spots | 找出盲點

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Would you like to enable them? | 要啟用嗎？

  [Y] ⭐ Recommended (exclude Expert Panel for speed) | 推薦
  [A] 🔥 All five enabled | 全部啟用
  [C] ⚙️ Custom configuration | 自訂配置
  [S] ⏭️ Skip for now (use /settings anytime) | 暫時跳過

> Enter your choice | 輸入選擇: _
"""
    
    def get_preset_menu(self) -> str:
        """
        Get the preset selection menu.
        取得預設選擇選單。
        """
        self._state = SetupState.PRESET_SELECTION
        
        lines = [
            "",
            "╭─────────────────────────────────────────────────────────╮",
            "│  ⚙️ Choose a Preset | 選擇預設配置                       │",
            "╰─────────────────────────────────────────────────────────╯",
            "",
        ]
        
        for i, preset in enumerate(self._presets, 1):
            emojis = preset.get_enabled_emojis()
            lines.append(f"  [{i}] {preset.display_name}")
            lines.append(f"      {preset.description}")
            lines.append(f"      Enabled: {emojis if emojis else '(none)'}")
            lines.append("")
        
        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "> Enter number (1-7) or [B] Back | 輸入數字或 [B] 返回: _",
        ])
        
        return "\n".join(lines)
    
    def get_custom_menu(self) -> str:
        """
        Get custom configuration menu.
        取得自訂配置選單。
        """
        self._state = SetupState.CUSTOM_CONFIG
        
        lines = [
            "",
            "╭─────────────────────────────────────────────────────────╮",
            "│  ⚙️ Custom Configuration | 自訂配置                      │",
            "╰─────────────────────────────────────────────────────────╯",
            "",
            "Toggle hacks on/off by entering their number:",
            "輸入數字切換啟用/禁用：",
            "",
        ]
        
        all_hacks = ["clarify", "web_backed", "self_grade", "expert_panel", "devils_advocate"]
        
        for i, hack_id in enumerate(all_hacks, 1):
            info = self.HACK_INFO[hack_id]
            status = "✓" if hack_id in self._config.enabled_hacks else "○"
            lines.append(f"  [{i}] {status} {info['emoji']} {info['name_en']} | {info['name_zh']} ({info['milestone']})")
        
        lines.extend([
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "  [D] Done | 完成",
            "  [R] Reset to recommended | 重設為推薦",
            "  [B] Back | 返回",
            "",
            "> Enter choice | 輸入選擇: _",
        ])
        
        return "\n".join(lines)
    
    def process_input(self, user_input: str) -> tuple[str, bool]:
        """
        Process user input and return next message.
        處理用戶輸入並返回下一個訊息。
        
        Args:
            user_input: User's input | 用戶輸入
            
        Returns:
            Tuple of (response message, is_complete) | (回應訊息, 是否完成)
        """
        user_input = user_input.strip().upper()
        
        if self._state == SetupState.WELCOME:
            return self._process_welcome_input(user_input)
        elif self._state == SetupState.PRESET_SELECTION:
            return self._process_preset_input(user_input)
        elif self._state == SetupState.CUSTOM_CONFIG:
            return self._process_custom_input(user_input)
        
        return self.get_welcome_message(), False
    
    def _process_welcome_input(self, user_input: str) -> tuple[str, bool]:
        """Process welcome screen input."""
        if user_input in ("Y", "YES", "1"):
            return self.apply_preset("recommended")
        elif user_input in ("A", "ALL", "2"):
            return self.apply_preset("all")
        elif user_input in ("C", "CUSTOM", "3"):
            # Initialize with recommended for custom
            self._config.enabled_hacks = get_recommended_preset().enabled_hacks.copy()
            return self.get_custom_menu(), False
        elif user_input in ("S", "SKIP", "4"):
            return self.apply_preset("none")
        else:
            return "❌ Invalid input. Please enter Y, A, C, or S.\n\n" + self.get_welcome_message(), False
    
    def _process_preset_input(self, user_input: str) -> tuple[str, bool]:
        """Process preset selection input."""
        if user_input == "B":
            return self.get_welcome_message(), False
        
        try:
            idx = int(user_input) - 1
            if 0 <= idx < len(self._presets):
                return self.apply_preset(self._presets[idx].id)
        except ValueError:
            pass
        
        return "❌ Invalid input. Enter 1-7 or B.\n" + self.get_preset_menu(), False
    
    def _process_custom_input(self, user_input: str) -> tuple[str, bool]:
        """Process custom configuration input."""
        if user_input == "D":
            self._config.preset_used = "custom"
            return self._complete_setup()
        elif user_input == "R":
            self._config.enabled_hacks = get_recommended_preset().enabled_hacks.copy()
            return self.get_custom_menu(), False
        elif user_input == "B":
            return self.get_welcome_message(), False
        
        try:
            idx = int(user_input) - 1
            all_hacks = ["clarify", "web_backed", "self_grade", "expert_panel", "devils_advocate"]
            if 0 <= idx < len(all_hacks):
                hack_id = all_hacks[idx]
                if hack_id in self._config.enabled_hacks:
                    self._config.enabled_hacks.remove(hack_id)
                else:
                    self._config.enabled_hacks.append(hack_id)
                return self.get_custom_menu(), False
        except ValueError:
            pass
        
        return "❌ Invalid input. Enter 1-5, D, R, or B.\n" + self.get_custom_menu(), False
    
    def apply_preset(self, preset_id: str) -> tuple[str, bool]:
        """
        Apply a preset configuration.
        套用預設配置。
        
        Args:
            preset_id: Preset identifier | 預設識別符
            
        Returns:
            Tuple of (confirmation message, is_complete) | (確認訊息, 是否完成)
        """
        preset = get_preset_by_id(preset_id)
        if not preset:
            return f"❌ Unknown preset: {preset_id}", False
        
        self._config.enabled_hacks = preset.enabled_hacks.copy()
        self._config.preset_used = preset_id
        
        return self._complete_setup()
    
    def _complete_setup(self) -> tuple[str, bool]:
        """Complete the setup process."""
        self._state = SetupState.COMPLETED
        self._config.setup_completed = True
        
        # Save config
        self._config.save(self._config_path)
        
        # Callback
        if self._on_complete:
            self._on_complete(self._config)
        
        # Build confirmation message
        enabled_emojis = []
        for hack_id in self._config.enabled_hacks:
            info = self.HACK_INFO.get(hack_id, {})
            enabled_emojis.append(info.get("emoji", "○"))
        
        emojis_str = " ".join(enabled_emojis) if enabled_emojis else "(none)"
        count = len(self._config.enabled_hacks)
        
        return f"""
╭─────────────────────────────────────────────────────────╮
│  ✅ Setup Complete! | 設定完成！                         │
╰─────────────────────────────────────────────────────────╯

Enabled hacks ({count}/5): {emojis_str}
已啟用的技巧：

{'  ' + '  '.join(f"{self.HACK_INFO[h]['emoji']} {self.HACK_INFO[h]['name_en']}" for h in self._config.enabled_hacks) if self._config.enabled_hacks else '  (No hacks enabled | 未啟用任何技巧)'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Tips | 提示:
   • Use /settings to change configuration anytime
     隨時使用 /settings 修改配置
   • Progress indicator will show: {emojis_str}
     進度指示器將顯示啟用的技巧

You're all set! Start using commands like:
您已準備就緒！開始使用指令，例如：

  /analyze-data @file:data.csv
  /summarize-doc @url:https://example.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""", True
    
    def get_settings_command_output(self) -> str:
        """
        Get output for /settings command.
        取得 /settings 指令的輸出。
        """
        existing = SetupConfig.load(self._config_path)
        if existing and existing.setup_completed:
            self._config = existing
        
        return self.get_custom_menu()
    
    @property
    def config(self) -> SetupConfig:
        """Get current configuration."""
        return self._config
    
    @property
    def state(self) -> SetupState:
        """Get current state."""
        return self._state
