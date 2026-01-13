"""
SAD System - SLASH@DASH Smart Command System

萬用 LLM 對話指令集
"""

__version__ = "0.1.0"
__author__ = "Yusei"

from .core.parser import CommandParser
from .core.registry import CommandRegistry, register_command
from .sabe.protocol import SABEProtocol

__all__ = [
    "CommandParser",
    "CommandRegistry", 
    "register_command",
    "SABEProtocol",
]
