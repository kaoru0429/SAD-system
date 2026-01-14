"""
Progress Hacks Module - 五言絕句

Auto-inject quality-enhancing prompts at progress milestones.
在進度里程碑自動注入品質提升附言。
"""

from .hacks import PromptHack, load_hacks
from .tracker import ProgressTracker, Milestone
from .injector import HackInjector
from .setup import SetupWizard, SetupConfig, Preset, get_presets

__all__ = [
    "PromptHack",
    "load_hacks",
    "ProgressTracker",
    "Milestone",
    "HackInjector",
    "SetupWizard",
    "SetupConfig",
    "Preset",
    "get_presets",
]

