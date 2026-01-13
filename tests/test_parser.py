"""
Tests for Command Parser
"""

import pytest
from src.core.parser import (
    CommandParser,
    ParsedCommand,
    ParseError,
    ParseErrorType,
    InputObject,
)


class TestCommandParser:
    """測試指令解析器"""
    
    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()
    
    def test_parse_simple_command(self, parser: CommandParser) -> None:
        """測試解析簡單指令"""
        result = parser.parse("/list-files")
        
        assert result.is_valid
        assert result.command_name == "list-files"
        assert result.verb == "list"
        assert result.noun == "files"
        assert result.input_object is None
        assert result.parameters == {}
    
    def test_parse_command_with_input(self, parser: CommandParser) -> None:
        """測試解析帶輸入的指令"""
        result = parser.parse("/analyze-data @file:sales.csv")
        
        assert result.is_valid
        assert result.command_name == "analyze-data"
        assert result.input_object is not None
        assert result.input_object.input_type == "file"
        assert result.input_object.identifier == "sales.csv"
    
    def test_parse_command_with_parameters(self, parser: CommandParser) -> None:
        """測試解析帶參數的指令"""
        result = parser.parse("/convert-file @file:data.json --to csv --encoding utf-8")
        
        assert result.is_valid
        assert result.command_name == "convert-file"
        assert result.parameters["to"] == "csv"
        assert result.parameters["encoding"] == "utf-8"
    
    def test_parse_command_with_flag(self, parser: CommandParser) -> None:
        """測試解析帶布林標記的指令"""
        result = parser.parse("/deploy-site @site:myapp --backup")
        
        assert result.is_valid
        assert result.parameters.get("backup") is True
    
    def test_parse_command_with_numeric_param(self, parser: CommandParser) -> None:
        """測試解析數值參數"""
        result = parser.parse("/analyze-data --limit 100 --ratio 0.5")
        
        assert result.is_valid
        assert result.parameters["limit"] == 100
        assert result.parameters["ratio"] == 0.5
    
    def test_parse_invalid_command(self, parser: CommandParser) -> None:
        """測試解析無效指令"""
        result = parser.parse("invalid command")
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert result.errors[0].error_type == ParseErrorType.MISSING_COMMAND
    
    def test_parse_url_input(self, parser: CommandParser) -> None:
        """測試解析 URL 輸入"""
        result = parser.parse("/summarize-doc @url:https://example.com/doc.pdf")
        
        assert result.is_valid
        assert result.input_object.input_type == "url"
        assert result.input_object.identifier == "https://example.com/doc.pdf"
    
    def test_cache_hit(self, parser: CommandParser) -> None:
        """測試快取命中"""
        cmd = "/list-files"
        
        result1 = parser.parse(cmd)
        result2 = parser.parse(cmd)
        
        assert result1 is result2  # 應該是同一個物件
    
    def test_clear_cache(self, parser: CommandParser) -> None:
        """測試清除快取"""
        cmd = "/list-files"
        
        result1 = parser.parse(cmd)
        parser.clear_cache()
        result2 = parser.parse(cmd)
        
        assert result1 is not result2  # 應該是不同物件


class TestParsedCommand:
    """測試 ParsedCommand"""
    
    def test_str_representation(self) -> None:
        """測試字串表示"""
        cmd = ParsedCommand(
            raw_input="/analyze-data @file:test.csv --format markdown",
            command_name="analyze-data",
            verb="analyze",
            noun="data",
            input_object=InputObject(
                input_type="file",
                identifier="test.csv",
                raw="@file:test.csv"
            ),
            parameters={"format": "markdown"}
        )
        
        result = str(cmd)
        assert "/analyze-data" in result
        assert "@file:test.csv" in result
        assert "--format markdown" in result


class TestInputObject:
    """測試 InputObject"""
    
    def test_str_representation(self) -> None:
        """測試字串表示"""
        obj = InputObject(
            input_type="file",
            identifier="test.csv",
            raw="@file:test.csv"
        )
        
        assert str(obj) == "@file:test.csv"
