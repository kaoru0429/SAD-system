"""
Setup Module - 首次對話設定

First-run setup flow for configuring Five Hacks preferences.
首次執行設定流程，用於配置五言絕句偏好。
"""

from .wizard import SetupWizard, SetupConfig
from .presets import Preset, get_presets

__all__ = [
    "SetupWizard",
    "SetupConfig", 
    "Preset",
    "get_presets",
]
