"""
SAD System v1.0 - Main Package
SAD 系統 v1.0 - 主要套件

Universal LLM Command Interface with S.A.B.E. Protocol and Five Hacks.
萬用 LLM 指令介面，整合 S.A.B.E. 協議與五言絕句。
"""

__version__ = "1.0.0"
__author__ = "Yusei"

from .core.parser import CommandParser
from .core.registry import CommandRegistry, register_command
from .mapping.verb_mapper import VerbMapper
from .sabe.protocol import SABEProtocol, SABEResponse, SABEMode
from .progress_hacks import (
    ProgressTracker,
    HackInjector,
    PromptHack,
    load_hacks,
    SetupWizard,
    SetupConfig,
)
from .undo import (
    HistoryStack,
    CommandSnapshot,
    UndoCommand,
    RedoCommand,
    HistoryCommand,
)
from .integration import SABEHacksIntegration, create_integration

__all__ = [
    # Version
    "__version__",
    
    # Core
    "CommandParser",
    "CommandRegistry",
    "register_command",
    
    # Mapping
    "VerbMapper",
    
    # SABE
    "SABEProtocol",
    "SABEResponse",
    "SABEMode",
    
    # Progress Hacks
    "ProgressTracker",
    "HackInjector",
    "PromptHack",
    "load_hacks",
    "SetupWizard",
    "SetupConfig",
    
    # Undo
    "HistoryStack",
    "CommandSnapshot",
    "UndoCommand",
    "RedoCommand",
    "HistoryCommand",
    
    # Integration
    "SABEHacksIntegration",
    "create_integration",
]
