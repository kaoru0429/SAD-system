"""
SABE-Hacks Integration - S.A.B.E. 與五言絕句整合

Integrates Five Prompt Hacks with S.A.B.E. protocol for enhanced AI interaction.
將五言絕句與 S.A.B.E. 協議整合，提升 AI 互動品質。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .sabe.protocol import SABEProtocol, SABEResponse, SABEMode, SABEStatus
from .progress_hacks import ProgressTracker, HackInjector, load_hacks, PromptHack
from .progress_hacks.setup import SetupWizard, SetupConfig
from .undo import HistoryStack, CommandSnapshot, get_history


@dataclass
class IntegrationConfig:
    """
    整合配置 | Integration Configuration
    
    Controls how SABE and Five Hacks work together.
    控制 S.A.B.E. 和五言絕句如何協同運作。
    """
    auto_suggest_clarify_on_ambiguous: bool = True
    enforce_devil_on_high_risk: bool = True
    recommend_all_hacks_on_large_task: bool = True
    record_to_history: bool = True
    show_progress_indicator: bool = True


class SABEHacksIntegration:
    """
    S.A.B.E. + 五言絕句整合 | SABE-Hacks Integration
    
    Combines S.A.B.E. safety protocol with Five Hacks quality enhancement.
    結合 S.A.B.E. 安全協議與五言絕句品質提升。
    
    Integration Points:
    - Mode A (Ambiguous): Auto-suggest Clarify hack
    - Mode C (Large Task): Recommend all hacks for thoroughness
    - Mode D (High Risk): Enforce Devil's Advocate hack
    
    Example:
        >>> integration = SABEHacksIntegration()
        >>> response, hacks = integration.check_and_enhance(command, prompt, context)
    """
    
    def __init__(
        self,
        sabe: SABEProtocol | None = None,
        tracker: ProgressTracker | None = None,
        injector: HackInjector | None = None,
        config: IntegrationConfig | None = None,
        history: HistoryStack | None = None
    ) -> None:
        """
        Initialize integration.
        初始化整合。
        
        Args:
            sabe: SABE protocol instance | S.A.B.E. 協議實例
            tracker: Progress tracker | 進度追蹤器
            injector: Hack injector | 技巧注入器
            config: Integration config | 整合配置
            history: History stack for undo | 恢復歷史堆疊
        """
        self._sabe = sabe or SABEProtocol()
        self._tracker = tracker or ProgressTracker()
        self._injector = injector or HackInjector()
        self._config = config or IntegrationConfig()
        self._history = history or get_history()
        self._hacks = load_hacks()
        self._setup_wizard = SetupWizard()
    
    def check_first_run(self) -> tuple[bool, str]:
        """
        Check if first-run setup is needed.
        檢查是否需要首次執行設定。
        
        Returns:
            Tuple of (is_first_run, welcome_message)
        """
        if self._setup_wizard.is_first_run():
            return True, self._setup_wizard.get_welcome_message()
        return False, ""
    
    def process_setup_input(self, user_input: str) -> tuple[str, bool]:
        """
        Process setup wizard input.
        處理設定精靈輸入。
        
        Args:
            user_input: User's input | 用戶輸入
            
        Returns:
            Tuple of (response, is_complete)
        """
        return self._setup_wizard.process_input(user_input)
    
    def check_and_enhance(
        self,
        command: Any,
        prompt: str,
        context: dict[str, Any] | None = None
    ) -> tuple[SABEResponse, str, list[PromptHack]]:
        """
        Check SABE triggers and apply relevant hacks.
        檢查 S.A.B.E. 觸發並套用相關技巧。
        
        Args:
            command: Parsed command | 解析後的指令
            prompt: Original prompt | 原始提示
            context: Execution context | 執行上下文
            
        Returns:
            Tuple of (sabe_response, enhanced_prompt, applied_hacks)
        """
        context = context or {}
        applied_hacks: list[PromptHack] = []
        enhanced_prompt = prompt
        
        # 1. Run SABE check
        sabe_response = self._sabe.check(command, context)
        
        # 2. Apply mode-specific hacks
        if sabe_response.triggered:
            mode_hacks = self._get_hacks_for_mode(sabe_response.mode)
            
            for hack in mode_hacks:
                if hack.enabled:
                    result = self._injector.inject(enhanced_prompt, hack)
                    enhanced_prompt = result.injected_prompt
                    applied_hacks.append(hack)
        
        # 3. Check progress milestones
        progress = context.get("progress", 0)
        if progress > 0:
            milestone_hack = self._tracker.update_progress(progress)
            if milestone_hack and milestone_hack not in applied_hacks:
                result = self._injector.inject(enhanced_prompt, milestone_hack)
                enhanced_prompt = result.injected_prompt
                applied_hacks.append(milestone_hack)
                self._tracker.mark_injected(milestone_hack.milestone)
        
        # 4. Record to history
        if self._config.record_to_history:
            snapshot = CommandSnapshot(
                id=f"cmd_{id(command)}",
                command_str=getattr(command, 'raw_input', str(command)),
                command_name=getattr(command, 'command_name', 'unknown')
            )
            self._history.push(snapshot)
        
        return sabe_response, enhanced_prompt, applied_hacks
    
    def _get_hacks_for_mode(self, mode: SABEMode | None) -> list[PromptHack]:
        """Get recommended hacks for a SABE mode."""
        if not mode:
            return []
        
        hack_map = {
            # Ambiguous: suggest clarify
            SABEMode.AMBIGUOUS_REPAIR: ["clarify"],
            
            # Error: clarify + self-grade
            SABEMode.ERROR_RECOVERY: ["clarify", "self_grade"],
            
            # Large task: all except expert (optional)
            SABEMode.LARGE_TASK_CONFIRM: ["clarify", "web_backed", "self_grade", "devils_advocate"]
            if self._config.recommend_all_hacks_on_large_task else ["self_grade"],
            
            # High risk: devil's advocate (enforced)
            SABEMode.HIGH_RISK_CONFIRM: ["devils_advocate"]
            if self._config.enforce_devil_on_high_risk else [],
            
            # Input missing: clarify
            SABEMode.INPUT_MISSING: ["clarify"],
        }
        
        hack_ids = hack_map.get(mode, [])
        return [h for h in self._hacks if h.id in hack_ids]
    
    def get_status(self) -> dict[str, Any]:
        """
        Get integration status.
        取得整合狀態。
        
        Returns:
            Status dictionary | 狀態字典
        """
        return {
            "progress": {
                "current": self._tracker.current_percentage,
                "indicator": self._tracker.get_compact_indicator(),
                "injected": self._tracker.get_injected_count(),
                "remaining": self._tracker.get_remaining_count(),
            },
            "history": {
                "can_undo": self._history.can_undo,
                "can_redo": self._history.can_redo,
                "undo_count": self._history.undo_count,
                "redo_count": self._history.redo_count,
            },
            "hacks": {
                "enabled": [h.id for h in self._hacks if h.enabled],
                "total": len(self._hacks),
            },
        }
    
    def format_status_display(self) -> str:
        """
        Format status for display.
        格式化狀態以供顯示。
        
        Returns:
            Formatted status string | 格式化的狀態字串
        """
        status = self.get_status()
        
        # Progress indicator
        progress_line = self._tracker.get_compact_indicator()
        
        # History status
        history = status["history"]
        history_line = f"History: ↩️{history['undo_count']} ↪️{history['redo_count']}"
        
        return f"""
╭─────────────────────────────────────────────────────────╮
│  SAD System v1.0 Status | 系統狀態                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  {progress_line:<51} │
│  {history_line:<51} │
│                                                         │
╰─────────────────────────────────────────────────────────╯
"""
    
    def reset_progress(self) -> None:
        """Reset progress tracker."""
        self._tracker.reset()
    
    def set_total_steps(self, total: int) -> None:
        """Set total steps for progress tracking."""
        self._tracker.set_total(total)


def create_integration(
    auto_setup: bool = True
) -> SABEHacksIntegration:
    """
    Factory function to create integration.
    建立整合的工廠函數。
    
    Args:
        auto_setup: Run setup wizard if first run | 首次執行時自動執行設定精靈
        
    Returns:
        Configured SABEHacksIntegration | 已配置的整合實例
    """
    integration = SABEHacksIntegration()
    
    if auto_setup:
        is_first, message = integration.check_first_run()
        if is_first:
            print(message)
    
    return integration
