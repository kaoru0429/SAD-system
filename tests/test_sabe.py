"""
Tests for S.A.B.E. Protocol
"""

import pytest
from src.sabe.protocol import (
    SABEProtocol,
    SABEMode,
    SABEStatus,
    SABEResponse,
    Suggestion,
)
from src.sabe.triggers import TriggerChecker, TriggerType
from src.core.parser import CommandParser


class TestSABEProtocol:
    """測試 S.A.B.E. 協議"""
    
    @pytest.fixture
    def protocol(self) -> SABEProtocol:
        return SABEProtocol()
    
    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()
    
    def test_no_trigger_for_safe_command(
        self, protocol: SABEProtocol, parser: CommandParser
    ) -> None:
        """測試安全指令不觸發"""
        cmd = parser.parse("/list-files")
        response = protocol.check(cmd)
        
        assert not response.triggered
    
    def test_trigger_for_high_risk(
        self, protocol: SABEProtocol, parser: CommandParser
    ) -> None:
        """測試高風險指令觸發"""
        cmd = parser.parse("/delete-file @file:important.txt")
        response = protocol.check(cmd)
        
        assert response.triggered
        assert response.mode == SABEMode.HIGH_RISK_CONFIRM
    
    def test_trigger_for_deploy(
        self, protocol: SABEProtocol, parser: CommandParser
    ) -> None:
        """測試部署指令觸發"""
        cmd = parser.parse("/deploy-site @site:myapp")
        response = protocol.check(cmd)
        
        assert response.triggered
        assert response.mode == SABEMode.HIGH_RISK_CONFIRM
    
    def test_trigger_for_low_confidence(
        self, protocol: SABEProtocol, parser: CommandParser
    ) -> None:
        """測試低置信度觸發"""
        cmd = parser.parse("/figure-out @data:sales")
        context = {
            "mapping_confidence": 45.0,
            "candidates": [
                {"command": "analyze-data", "description": "分析", "confidence": 80},
            ]
        }
        
        response = protocol.check(cmd, context)
        
        assert response.triggered
        assert response.mode == SABEMode.AMBIGUOUS_REPAIR
    
    def test_trigger_for_input_error(
        self, protocol: SABEProtocol, parser: CommandParser
    ) -> None:
        """測試輸入錯誤觸發"""
        cmd = parser.parse("/analyze-data @file:nonexistent.csv")
        context = {
            "input_error": {"message": "檔案不存在"},
            "recent_files": ["file1.csv", "file2.csv"]
        }
        
        response = protocol.check(cmd, context)
        
        assert response.triggered
        assert response.mode == SABEMode.INPUT_MISSING
    
    def test_trigger_for_large_task(
        self, protocol: SABEProtocol, parser: CommandParser
    ) -> None:
        """測試大型任務觸發"""
        cmd = parser.parse("/full-workflow @file:data.csv --complete")
        context = {
            "estimated_tokens": 100000,
            "estimated_steps": 10,
            "workflow_steps": [f"Step {i}" for i in range(1, 11)]
        }
        
        response = protocol.check(cmd, context)
        
        assert response.triggered
        assert response.mode == SABEMode.LARGE_TASK_CONFIRM
    
    def test_format_prompt(self, protocol: SABEProtocol, parser: CommandParser) -> None:
        """測試格式化提示"""
        cmd = parser.parse("/delete-file @file:test.txt")
        response = protocol.check(cmd)
        
        prompt = response.format_prompt()
        
        assert "S.A.B.E." in prompt
        assert "高風險" in prompt or "HIGH_RISK" in prompt
    
    def test_process_response_confirm(
        self, protocol: SABEProtocol, parser: CommandParser
    ) -> None:
        """測試處理確認回應"""
        cmd = parser.parse("/delete-file @file:test.txt")
        response = protocol.check(cmd)
        
        updated = protocol.process_response(response, 1)
        
        assert updated.status == SABEStatus.CONFIRMED
        assert updated.selected_option == 1
    
    def test_process_response_cancel(
        self, protocol: SABEProtocol, parser: CommandParser
    ) -> None:
        """測試處理取消回應"""
        cmd = parser.parse("/delete-file @file:test.txt")
        response = protocol.check(cmd)
        
        updated = protocol.process_response(response, "cancel")
        
        assert updated.status == SABEStatus.CANCELLED
    
    def test_process_response_custom_command(
        self, protocol: SABEProtocol, parser: CommandParser
    ) -> None:
        """測試處理自訂指令回應"""
        cmd = parser.parse("/delete-file @file:test.txt")
        response = protocol.check(cmd)
        
        updated = protocol.process_response(response, "/backup-file @file:test.txt")
        
        assert updated.status == SABEStatus.MODIFIED


class TestTriggerChecker:
    """測試觸發檢查器"""
    
    @pytest.fixture
    def checker(self) -> TriggerChecker:
        return TriggerChecker()
    
    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()
    
    def test_check_high_risk(
        self, checker: TriggerChecker, parser: CommandParser
    ) -> None:
        """測試高風險檢查"""
        cmd = parser.parse("/delete-file @file:test.txt")
        result = checker.check_high_risk(cmd, {})
        
        assert result.triggered
        assert result.trigger_type == TriggerType.HIGH_RISK
        assert result.severity >= 8
    
    def test_check_ambiguous_verb(
        self, checker: TriggerChecker, parser: CommandParser
    ) -> None:
        """測試模糊動詞檢查"""
        cmd = parser.parse("/figure-out @data:sales")
        context = {"mapping_confidence": 50.0}
        
        result = checker.check_ambiguous_verb(cmd, context)
        
        assert result.triggered
        assert result.trigger_type == TriggerType.AMBIGUOUS_VERB
    
    def test_check_large_task_by_tokens(
        self, checker: TriggerChecker, parser: CommandParser
    ) -> None:
        """測試大型任務檢查（按 Token）"""
        cmd = parser.parse("/process-all")
        context = {"estimated_tokens": 60000}
        
        result = checker.check_large_task(cmd, context)
        
        assert result.triggered
        assert result.trigger_type == TriggerType.LARGE_TASK
    
    def test_check_large_task_by_steps(
        self, checker: TriggerChecker, parser: CommandParser
    ) -> None:
        """測試大型任務檢查（按步驟）"""
        cmd = parser.parse("/workflow")
        context = {"estimated_steps": 8}
        
        result = checker.check_large_task(cmd, context)
        
        assert result.triggered
    
    def test_check_all(
        self, checker: TriggerChecker, parser: CommandParser
    ) -> None:
        """測試檢查所有條件"""
        cmd = parser.parse("/delete-file @file:test.txt")
        context = {"estimated_tokens": 60000}
        
        results = checker.check_all(cmd, context)
        
        assert len(results) >= 1  # 至少高風險會觸發
    
    def test_check_highest_priority(
        self, checker: TriggerChecker, parser: CommandParser
    ) -> None:
        """測試取得最高優先級"""
        cmd = parser.parse("/destroy-all")
        context = {
            "mapping_confidence": 50.0,
            "estimated_tokens": 60000
        }
        
        result = checker.check_highest_priority(cmd, context)
        
        assert result.triggered
        # destroy 是最高風險的


class TestSuggestion:
    """測試建議項目"""
    
    def test_str_representation(self) -> None:
        """測試字串表示"""
        suggestion = Suggestion(
            index=1,
            command="/analyze-data",
            description="詳細分析",
            confidence=95.0
        )
        
        result = str(suggestion)
        
        assert "1." in result
        assert "詳細分析" in result
        assert "/analyze-data" in result
