"""
S.A.B.E. Protocol - Suggest & Ask Before Exec

智慧代理核心協議，確保零錯誤自動化
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from ..core.parser import ParsedCommand


class SABEMode(Enum):
    """S.A.B.E. 交互模式"""
    AMBIGUOUS_REPAIR = "A"      # 模糊指令修復
    ERROR_RECOVERY = "B"        # 錯誤自動恢復
    LARGE_TASK_CONFIRM = "C"    # 大型任務確認
    HIGH_RISK_CONFIRM = "D"     # 高風險操作確認
    INPUT_MISSING = "E"         # 輸入缺失


class SABEStatus(Enum):
    """S.A.B.E. 狀態"""
    PENDING = "pending"         # 等待用戶回應
    CONFIRMED = "confirmed"     # 用戶已確認
    CANCELLED = "cancelled"     # 用戶已取消
    MODIFIED = "modified"       # 用戶已修改
    TIMEOUT = "timeout"         # 超時


@dataclass
class Suggestion:
    """建議項目"""
    index: int
    command: str
    description: str
    confidence: float = 0.0
    risk_level: str = "low"
    
    def __str__(self) -> str:
        return f"{self.index}. {self.description}\n   ```{self.command}```"


@dataclass
class SABEResponse:
    """S.A.B.E. 協議回應"""
    triggered: bool
    mode: SABEMode | None = None
    original_command: ParsedCommand | None = None
    trigger_reason: str = ""
    suggestions: list[Suggestion] = field(default_factory=list)
    prompt_message: str = ""
    status: SABEStatus = SABEStatus.PENDING
    selected_option: int | str | None = None
    final_command: ParsedCommand | None = None
    
    @classmethod
    def no_trigger(cls) -> SABEResponse:
        """建立未觸發回應"""
        return cls(triggered=False)
    
    def format_prompt(self) -> str:
        """格式化提示訊息"""
        if not self.triggered:
            return ""
        
        lines = [
            "🛑 S.A.B.E. 協議觸發",
            "",
            f"📋 模式: {self._mode_name()}",
            f"❓ 原因: {self.trigger_reason}",
            "",
        ]
        
        if self.original_command:
            lines.append(f"📝 原始指令: `{self.original_command.raw_input}`")
            lines.append("")
        
        if self.suggestions:
            lines.append("🔍 智能建議:")
            for suggestion in self.suggestions:
                lines.append(str(suggestion))
                lines.append("")
        
        lines.append("❓ 請選擇選項編號，或輸入自訂指令:")
        
        return "\n".join(lines)
    
    def _mode_name(self) -> str:
        """取得模式名稱"""
        mode_names = {
            SABEMode.AMBIGUOUS_REPAIR: "模糊指令修復",
            SABEMode.ERROR_RECOVERY: "錯誤自動恢復",
            SABEMode.LARGE_TASK_CONFIRM: "大型任務確認",
            SABEMode.HIGH_RISK_CONFIRM: "高風險操作確認",
            SABEMode.INPUT_MISSING: "輸入缺失",
        }
        return mode_names.get(self.mode, "未知") if self.mode else "未知"


class SABEProtocol:
    """
    S.A.B.E. 協議處理器
    
    Suggest & Ask Before Exec - 在執行前提出建議並徵求確認
    
    Example:
        >>> protocol = SABEProtocol()
        >>> response = protocol.check(parsed_command, context)
        >>> if response.triggered:
        ...     print(response.format_prompt())
    """
    
    def __init__(
        self,
        mapping_threshold: float = 90.0,
        large_task_token_threshold: int = 50000,
        large_task_step_threshold: int = 5,
        max_suggestions: int = 5
    ) -> None:
        """
        初始化 S.A.B.E. 協議
        
        Args:
            mapping_threshold: 映射閾值（低於此值觸發）
            large_task_token_threshold: 大型任務 Token 閾值
            large_task_step_threshold: 大型任務步驟閾值
            max_suggestions: 最大建議數量
        """
        self.mapping_threshold = mapping_threshold
        self.large_task_token_threshold = large_task_token_threshold
        self.large_task_step_threshold = large_task_step_threshold
        self.max_suggestions = max_suggestions
        
        self._trigger_handlers: dict[SABEMode, Callable[..., SABEResponse]] = {
            SABEMode.AMBIGUOUS_REPAIR: self._handle_ambiguous,
            SABEMode.ERROR_RECOVERY: self._handle_error,
            SABEMode.LARGE_TASK_CONFIRM: self._handle_large_task,
            SABEMode.HIGH_RISK_CONFIRM: self._handle_high_risk,
            SABEMode.INPUT_MISSING: self._handle_input_missing,
        }
        
        # 高風險指令列表
        self._high_risk_verbs = {
            "deploy", "delete", "remove", "destroy", "overwrite",
            "publish", "release", "drop", "truncate"
        }
    
    def check(
        self,
        command: ParsedCommand,
        context: dict[str, Any] | None = None
    ) -> SABEResponse:
        """
        檢查是否需要觸發 S.A.B.E. 協議
        
        Args:
            command: 解析後的指令
            context: 上下文資訊
            
        Returns:
            S.A.B.E. 回應
        """
        context = context or {}
        
        # 檢查各種觸發條件
        
        # 1. 高風險操作
        if command.verb in self._high_risk_verbs:
            return self._handle_high_risk(command, context)
        
        # 2. 映射置信度低（模糊動詞）
        confidence = context.get("mapping_confidence", 100.0)
        if confidence < self.mapping_threshold:
            return self._handle_ambiguous(command, context)
        
        # 3. 輸入缺失或無效
        if context.get("input_error"):
            return self._handle_input_missing(command, context)
        
        # 4. 前一指令錯誤
        if context.get("previous_error"):
            return self._handle_error(command, context)
        
        # 5. 大型任務
        estimated_tokens = context.get("estimated_tokens", 0)
        estimated_steps = context.get("estimated_steps", 0)
        if (estimated_tokens > self.large_task_token_threshold or
            estimated_steps > self.large_task_step_threshold):
            return self._handle_large_task(command, context)
        
        # 無需觸發
        return SABEResponse.no_trigger()
    
    def _handle_ambiguous(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> SABEResponse:
        """處理模糊指令"""
        candidates = context.get("candidates", [])
        suggestions = []
        
        for i, candidate in enumerate(candidates[:self.max_suggestions], 1):
            suggestions.append(Suggestion(
                index=i,
                command=candidate.get("command", ""),
                description=candidate.get("description", ""),
                confidence=candidate.get("confidence", 0.0)
            ))
        
        return SABEResponse(
            triggered=True,
            mode=SABEMode.AMBIGUOUS_REPAIR,
            original_command=command,
            trigger_reason=f"動詞 '{command.verb}' 無法確定映射到標準指令",
            suggestions=suggestions,
            prompt_message="請選擇正確的指令"
        )
    
    def _handle_error(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> SABEResponse:
        """處理錯誤恢復"""
        previous_error = context.get("previous_error", {})
        recovery_options = context.get("recovery_options", [])
        
        suggestions = []
        for i, option in enumerate(recovery_options[:self.max_suggestions], 1):
            suggestions.append(Suggestion(
                index=i,
                command=option.get("command", ""),
                description=option.get("description", "")
            ))
        
        return SABEResponse(
            triggered=True,
            mode=SABEMode.ERROR_RECOVERY,
            original_command=command,
            trigger_reason=f"前一指令執行失敗: {previous_error.get('message', '未知錯誤')}",
            suggestions=suggestions,
            prompt_message="請選擇恢復選項"
        )
    
    def _handle_large_task(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> SABEResponse:
        """處理大型任務確認"""
        steps = context.get("workflow_steps", [])
        estimated_tokens = context.get("estimated_tokens", 0)
        
        step_list = "\n".join(f"  {i}. {step}" for i, step in enumerate(steps, 1))
        
        return SABEResponse(
            triggered=True,
            mode=SABEMode.LARGE_TASK_CONFIRM,
            original_command=command,
            trigger_reason=f"大型任務：預估 {len(steps)} 步驟, ~{estimated_tokens:,} tokens",
            suggestions=[
                Suggestion(1, "confirm", "確認執行完整流程"),
                Suggestion(2, "trim", "修剪工作流程"),
                Suggestion(3, "cancel", "取消執行"),
            ],
            prompt_message=f"工作流程:\n{step_list}\n\n確認執行？(Y/修剪/取消)"
        )
    
    def _handle_high_risk(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> SABEResponse:
        """處理高風險操作確認"""
        return SABEResponse(
            triggered=True,
            mode=SABEMode.HIGH_RISK_CONFIRM,
            original_command=command,
            trigger_reason=f"高風險操作：{command.verb} 是不可逆指令",
            suggestions=[
                Suggestion(1, "confirm", "確認執行（不可撤銷）", risk_level="high"),
                Suggestion(2, "cancel", "取消操作"),
                Suggestion(3, "backup", "先備份再執行"),
            ],
            prompt_message="⚠️ 此操作不可撤銷，確認執行？"
        )
    
    def _handle_input_missing(
        self,
        command: ParsedCommand,
        context: dict[str, Any]
    ) -> SABEResponse:
        """處理輸入缺失"""
        input_error = context.get("input_error", {})
        recent_files = context.get("recent_files", [])
        
        suggestions = []
        for i, file in enumerate(recent_files[:3], 1):
            suggestions.append(Suggestion(
                index=i,
                command=f"/{command.command_name} @file:{file}",
                description=f"使用最近檔案: {file}"
            ))
        
        suggestions.append(Suggestion(
            index=len(suggestions) + 1,
            command="upload",
            description="上傳新檔案"
        ))
        
        return SABEResponse(
            triggered=True,
            mode=SABEMode.INPUT_MISSING,
            original_command=command,
            trigger_reason=input_error.get("message", "輸入對象缺失或無效"),
            suggestions=suggestions,
            prompt_message="請選擇輸入來源"
        )
    
    def process_response(
        self,
        sabe_response: SABEResponse,
        user_input: str | int
    ) -> SABEResponse:
        """
        處理用戶回應
        
        Args:
            sabe_response: 原始 S.A.B.E. 回應
            user_input: 用戶輸入（編號或指令）
            
        Returns:
            更新後的 S.A.B.E. 回應
        """
        # 處理取消
        if isinstance(user_input, str) and user_input.lower() in ("cancel", "取消", "n", "no"):
            sabe_response.status = SABEStatus.CANCELLED
            return sabe_response
        
        # 處理數字選擇
        if isinstance(user_input, int) or (isinstance(user_input, str) and user_input.isdigit()):
            index = int(user_input)
            sabe_response.selected_option = index
            
            if 1 <= index <= len(sabe_response.suggestions):
                selected = sabe_response.suggestions[index - 1]
                sabe_response.status = SABEStatus.CONFIRMED
                # TODO: 解析 selected.command 為 ParsedCommand
            else:
                sabe_response.status = SABEStatus.PENDING
                
            return sabe_response
        
        # 處理自訂指令
        if isinstance(user_input, str) and user_input.startswith("/"):
            sabe_response.status = SABEStatus.MODIFIED
            sabe_response.selected_option = user_input
            # TODO: 解析新指令
            return sabe_response
        
        # 其他情況保持 pending
        return sabe_response


# 測試
if __name__ == "__main__":
    from ..core.parser import CommandParser
    
    parser = CommandParser()
    protocol = SABEProtocol()
    
    # 測試高風險操作
    cmd = parser.parse("/delete-file @file:important.txt")
    response = protocol.check(cmd)
    
    if response.triggered:
        print(response.format_prompt())
    
    # 測試模糊指令
    cmd = parser.parse("/figure-out @data:sales")
    context = {
        "mapping_confidence": 45.0,
        "candidates": [
            {"command": "/analyze-data", "description": "詳細分析", "confidence": 80},
            {"command": "/summarize-doc", "description": "摘要生成", "confidence": 60},
        ]
    }
    response = protocol.check(cmd, context)
    
    if response.triggered:
        print("\n" + "="*50 + "\n")
        print(response.format_prompt())
