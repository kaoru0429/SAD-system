"""
Suggestion Generator - 建議生成器

根據上下文生成智能建議
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.parser import ParsedCommand
from ..core.registry import get_registry, CommandSpec


@dataclass
class SuggestionItem:
    """建議項目"""
    index: int
    command: str
    description: str
    confidence: float
    risk_level: str = "low"
    estimated_tokens: int = 0


class SuggestionGenerator:
    """
    建議生成器
    
    根據上下文和指令歷史生成智能建議
    
    Example:
        >>> generator = SuggestionGenerator()
        >>> suggestions = generator.generate_for_ambiguous(command, candidates)
    """
    
    def __init__(self, max_suggestions: int = 5) -> None:
        """
        初始化建議生成器
        
        Args:
            max_suggestions: 最大建議數量
        """
        self.max_suggestions = max_suggestions
        self._registry = get_registry()
    
    def generate_for_ambiguous(
        self,
        command: ParsedCommand,
        candidates: list[dict[str, Any]]
    ) -> list[SuggestionItem]:
        """
        為模糊指令生成建議
        
        Args:
            command: 原始指令
            candidates: 候選指令列表
            
        Returns:
            建議列表
        """
        suggestions: list[SuggestionItem] = []
        
        # 按置信度排序候選
        sorted_candidates = sorted(
            candidates,
            key=lambda c: c.get("confidence", 0),
            reverse=True
        )
        
        for i, candidate in enumerate(sorted_candidates[:self.max_suggestions], 1):
            # 重建完整指令
            new_command = f"/{candidate['command']}"
            if command.input_object:
                new_command += f" {command.input_object}"
            for key, value in command.parameters.items():
                if isinstance(value, bool) and value:
                    new_command += f" --{key.replace('_', '-')}"
                else:
                    new_command += f" --{key.replace('_', '-')} {value}"
            
            suggestions.append(SuggestionItem(
                index=i,
                command=new_command,
                description=candidate.get("description", ""),
                confidence=candidate.get("confidence", 0.0),
                risk_level=candidate.get("risk_level", "low")
            ))
        
        return suggestions
    
    def generate_for_input_error(
        self,
        command: ParsedCommand,
        recent_inputs: list[str],
        error_type: str
    ) -> list[SuggestionItem]:
        """
        為輸入錯誤生成建議
        
        Args:
            command: 原始指令
            recent_inputs: 最近使用的輸入列表
            error_type: 錯誤類型
            
        Returns:
            建議列表
        """
        suggestions: list[SuggestionItem] = []
        
        # 根據最近輸入生成建議
        for i, recent_input in enumerate(recent_inputs[:3], 1):
            new_command = f"/{command.command_name} @file:{recent_input}"
            for key, value in command.parameters.items():
                if isinstance(value, bool) and value:
                    new_command += f" --{key.replace('_', '-')}"
                else:
                    new_command += f" --{key.replace('_', '-')} {value}"
            
            suggestions.append(SuggestionItem(
                index=i,
                command=new_command,
                description=f"使用最近檔案: {recent_input}",
                confidence=80.0 - (i * 10)
            ))
        
        # 添加上傳新檔案選項
        suggestions.append(SuggestionItem(
            index=len(suggestions) + 1,
            command="/upload-file",
            description="上傳新檔案",
            confidence=60.0
        ))
        
        # 添加列出檔案選項
        suggestions.append(SuggestionItem(
            index=len(suggestions) + 1,
            command="/list-files",
            description="列出可用檔案",
            confidence=50.0
        ))
        
        return suggestions[:self.max_suggestions]
    
    def generate_for_high_risk(
        self,
        command: ParsedCommand,
        spec: CommandSpec | None
    ) -> list[SuggestionItem]:
        """
        為高風險操作生成建議
        
        Args:
            command: 原始指令
            spec: 指令規格
            
        Returns:
            建議列表
        """
        suggestions: list[SuggestionItem] = []
        
        # 確認執行
        suggestions.append(SuggestionItem(
            index=1,
            command=command.raw_input,
            description="確認執行（不可撤銷）",
            confidence=100.0,
            risk_level="high"
        ))
        
        # 取消操作
        suggestions.append(SuggestionItem(
            index=2,
            command="cancel",
            description="取消操作",
            confidence=100.0,
            risk_level="low"
        ))
        
        # 如果是刪除操作，建議先備份
        if command.verb in ("delete", "remove", "destroy"):
            backup_cmd = f"/backup {command.input_object}" if command.input_object else "/backup"
            suggestions.append(SuggestionItem(
                index=3,
                command=backup_cmd + " && " + command.raw_input,
                description="先備份再執行",
                confidence=90.0,
                risk_level="medium"
            ))
        
        return suggestions
    
    def generate_for_large_task(
        self,
        command: ParsedCommand,
        workflow_steps: list[str],
        estimated_tokens: int
    ) -> list[SuggestionItem]:
        """
        為大型任務生成建議
        
        Args:
            command: 原始指令
            workflow_steps: 工作流程步驟
            estimated_tokens: 預估 Token 數
            
        Returns:
            建議列表
        """
        suggestions: list[SuggestionItem] = []
        
        # 確認完整執行
        suggestions.append(SuggestionItem(
            index=1,
            command=command.raw_input,
            description=f"執行完整流程 ({len(workflow_steps)} 步驟)",
            confidence=100.0,
            estimated_tokens=estimated_tokens
        ))
        
        # 修剪工作流程
        suggestions.append(SuggestionItem(
            index=2,
            command="trim",
            description="修剪工作流程（選擇部分步驟）",
            confidence=80.0
        ))
        
        # 分批執行
        if len(workflow_steps) > 5:
            half = len(workflow_steps) // 2
            suggestions.append(SuggestionItem(
                index=3,
                command=f"{command.raw_input} --steps 1-{half}",
                description=f"分批執行：先執行前 {half} 步",
                confidence=70.0,
                estimated_tokens=estimated_tokens // 2
            ))
        
        # 取消
        suggestions.append(SuggestionItem(
            index=len(suggestions) + 1,
            command="cancel",
            description="取消執行",
            confidence=100.0
        ))
        
        return suggestions
    
    def generate_for_error_recovery(
        self,
        command: ParsedCommand,
        error_info: dict[str, Any],
        recovery_options: list[dict[str, Any]]
    ) -> list[SuggestionItem]:
        """
        為錯誤恢復生成建議
        
        Args:
            command: 原始指令
            error_info: 錯誤資訊
            recovery_options: 恢復選項
            
        Returns:
            建議列表
        """
        suggestions: list[SuggestionItem] = []
        
        for i, option in enumerate(recovery_options[:self.max_suggestions - 1], 1):
            suggestions.append(SuggestionItem(
                index=i,
                command=option.get("command", ""),
                description=option.get("description", ""),
                confidence=option.get("confidence", 50.0)
            ))
        
        # 重試原始指令
        suggestions.append(SuggestionItem(
            index=len(suggestions) + 1,
            command=command.raw_input,
            description="重試原始指令",
            confidence=30.0
        ))
        
        return suggestions
