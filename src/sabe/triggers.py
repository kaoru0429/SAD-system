"""
Trigger Checker - S.A.B.E. 觸發條件檢查器
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..core.parser import ParsedCommand


class TriggerType(Enum):
    """觸發類型"""
    NONE = "none"
    AMBIGUOUS_VERB = "ambiguous_verb"
    INPUT_ERROR = "input_error"
    HIGH_RISK = "high_risk"
    LARGE_TASK = "large_task"
    PREVIOUS_ERROR = "previous_error"
    MISSING_REQUIRED = "missing_required"


@dataclass
class TriggerResult:
    """觸發檢查結果"""
    triggered: bool
    trigger_type: TriggerType
    severity: int  # 1-10
    details: dict[str, Any]
    
    @classmethod
    def no_trigger(cls) -> TriggerResult:
        """無觸發"""
        return cls(
            triggered=False,
            trigger_type=TriggerType.NONE,
            severity=0,
            details={}
        )


class TriggerChecker:
    """
    觸發條件檢查器
    
    檢查各種可能觸發 S.A.B.E. 協議的條件
    
    Example:
        >>> checker = TriggerChecker()
        >>> result = checker.check_all(command, context)
    """
    
    # 高風險動詞
    HIGH_RISK_VERBS = {
        "deploy": 8,
        "delete": 9,
        "remove": 8,
        "destroy": 10,
        "overwrite": 7,
        "publish": 6,
        "release": 6,
        "drop": 9,
        "truncate": 9,
    }
    
    def __init__(
        self,
        mapping_threshold: float = 90.0,
        token_threshold: int = 50000,
        step_threshold: int = 5
    ) -> None:
        """
        初始化觸發檢查器
        
        Args:
            mapping_threshold: 映射置信度閾值
            token_threshold: 大型任務 Token 閾值
            step_threshold: 大型任務步驟閾值
        """
        self.mapping_threshold = mapping_threshold
        self.token_threshold = token_threshold
        self.step_threshold = step_threshold
    
    def check_all(
        self,
        command: ParsedCommand,
        context: dict[str, Any] | None = None
    ) -> list[TriggerResult]:
        """
        檢查所有觸發條件
        
        Args:
            command: 解析後的指令
            context: 上下文資訊
            
        Returns:
            所有觸發結果列表
        """
        context = context or {}
        results: list[TriggerResult] = []
        
        # 依優先順序檢查
        checkers = [
            self.check_high_risk,
            self.check_ambiguous_verb,
            self.check_input_error,
            self.check_previous_error,
            self.check_large_task,
            self.check_missing_required,
        ]
        
        for checker in checkers:
            result = checker(command, context)
            if result.triggered:
                results.append(result)
        
        return results
    
    def check_highest_priority(
        self,
        command: ParsedCommand,
        context: dict[str, Any] | None = None
    ) -> TriggerResult:
        """
        檢查最高優先級的觸發條件
        
        Args:
            command: 解析後的指令
            context: 上下文資訊
            
        Returns:
            最高優先級的觸發結果
        """
        results = self.check_all(command, context)
        
        if not results:
            return TriggerResult.no_trigger()
        
        # 按嚴重程度排序
        results.sort(key=lambda r: r.severity, reverse=True)
        return results[0]
    
    def check_high_risk(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> TriggerResult:
        """檢查高風險操作"""
        verb = command.verb
        
        if verb in self.HIGH_RISK_VERBS:
            return TriggerResult(
                triggered=True,
                trigger_type=TriggerType.HIGH_RISK,
                severity=self.HIGH_RISK_VERBS[verb],
                details={
                    "verb": verb,
                    "command": command.command_name,
                    "reason": f"'{verb}' 是高風險不可逆操作"
                }
            )
        
        return TriggerResult.no_trigger()
    
    def check_ambiguous_verb(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> TriggerResult:
        """檢查模糊動詞"""
        confidence = context.get("mapping_confidence", 100.0)
        
        if confidence < self.mapping_threshold:
            return TriggerResult(
                triggered=True,
                trigger_type=TriggerType.AMBIGUOUS_VERB,
                severity=int((self.mapping_threshold - confidence) / 10) + 3,
                details={
                    "verb": command.verb,
                    "confidence": confidence,
                    "threshold": self.mapping_threshold,
                    "candidates": context.get("candidates", [])
                }
            )
        
        return TriggerResult.no_trigger()
    
    def check_input_error(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> TriggerResult:
        """檢查輸入錯誤"""
        input_error = context.get("input_error")
        
        if input_error:
            return TriggerResult(
                triggered=True,
                trigger_type=TriggerType.INPUT_ERROR,
                severity=5,
                details={
                    "error": input_error,
                    "input_object": str(command.input_object) if command.input_object else None
                }
            )
        
        return TriggerResult.no_trigger()
    
    def check_previous_error(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> TriggerResult:
        """檢查前一指令錯誤"""
        previous_error = context.get("previous_error")
        
        if previous_error:
            return TriggerResult(
                triggered=True,
                trigger_type=TriggerType.PREVIOUS_ERROR,
                severity=6,
                details={
                    "previous_error": previous_error,
                    "recovery_options": context.get("recovery_options", [])
                }
            )
        
        return TriggerResult.no_trigger()
    
    def check_large_task(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> TriggerResult:
        """檢查大型任務"""
        estimated_tokens = context.get("estimated_tokens", 0)
        estimated_steps = context.get("estimated_steps", 0)
        
        is_large_by_tokens = estimated_tokens > self.token_threshold
        is_large_by_steps = estimated_steps > self.step_threshold
        
        if is_large_by_tokens or is_large_by_steps:
            return TriggerResult(
                triggered=True,
                trigger_type=TriggerType.LARGE_TASK,
                severity=4,
                details={
                    "estimated_tokens": estimated_tokens,
                    "estimated_steps": estimated_steps,
                    "workflow_steps": context.get("workflow_steps", []),
                    "triggered_by": "tokens" if is_large_by_tokens else "steps"
                }
            )
        
        return TriggerResult.no_trigger()
    
    def check_missing_required(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> TriggerResult:
        """檢查缺少必填項"""
        missing_params = context.get("missing_required_params", [])
        
        if missing_params:
            return TriggerResult(
                triggered=True,
                trigger_type=TriggerType.MISSING_REQUIRED,
                severity=5,
                details={
                    "missing_params": missing_params
                }
            )
        
        return TriggerResult.no_trigger()
