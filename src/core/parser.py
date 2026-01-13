"""
Command Parser - 指令解析器

解析 SLASH@DASH 語法結構：
/指令名 @輸入 --參數 值
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ParseErrorType(Enum):
    """解析錯誤類型"""
    INVALID_SYNTAX = "invalid_syntax"
    MISSING_COMMAND = "missing_command"
    INVALID_COMMAND_NAME = "invalid_command_name"
    INVALID_INPUT_FORMAT = "invalid_input_format"
    INVALID_PARAMETER = "invalid_parameter"
    DUPLICATE_PARAMETER = "duplicate_parameter"


@dataclass
class ParseError:
    """解析錯誤"""
    error_type: ParseErrorType
    message: str
    position: int | None = None
    suggestion: str | None = None


@dataclass
class InputObject:
    """輸入對象 @type:id"""
    input_type: str
    identifier: str
    raw: str
    
    def __str__(self) -> str:
        return f"@{self.input_type}:{self.identifier}"


@dataclass
class Parameter:
    """參數 --key value"""
    key: str
    value: str | bool | int | float
    
    def __str__(self) -> str:
        if isinstance(self.value, bool):
            return f"--{self.key}"
        return f"--{self.key} {self.value}"


@dataclass
class ParsedCommand:
    """解析後的指令結構"""
    raw_input: str
    command_name: str
    verb: str
    noun: str
    input_object: InputObject | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True
    errors: list[ParseError] = field(default_factory=list)
    
    def __str__(self) -> str:
        parts = [f"/{self.command_name}"]
        if self.input_object:
            parts.append(str(self.input_object))
        for key, value in self.parameters.items():
            if isinstance(value, bool) and value:
                parts.append(f"--{key}")
            else:
                parts.append(f"--{key} {value}")
        return " ".join(parts)


class CommandParser:
    """
    SLASH@DASH 指令解析器
    
    解析格式: /指令名 @輸入 --參數 值
    
    Example:
        >>> parser = CommandParser()
        >>> result = parser.parse("/analyze-data @file:sales.csv --format markdown")
        >>> print(result.command_name)
        'analyze-data'
        >>> print(result.input_object)
        '@file:sales.csv'
    """
    
    # 正則表達式模式
    COMMAND_PATTERN = re.compile(r"^/([a-z]+(?:-[a-z]+)*)")
    INPUT_PATTERN = re.compile(r"@([a-z]+):([^\s]+)")
    PARAM_PATTERN = re.compile(r"--([a-z]+(?:-[a-z]+)*)\s+([^\s-][^\s]*)")
    FLAG_PATTERN = re.compile(r"--([a-z]+(?:-[a-z]+)*)(?=\s+--|$|\s*$)")
    
    def __init__(self) -> None:
        self._cache: dict[str, ParsedCommand] = {}
    
    def parse(self, input_str: str) -> ParsedCommand:
        """
        解析輸入字串為結構化指令
        
        Args:
            input_str: 原始輸入字串
            
        Returns:
            ParsedCommand 結構化指令物件
        """
        input_str = input_str.strip()
        
        # 檢查快取
        if input_str in self._cache:
            return self._cache[input_str]
        
        errors: list[ParseError] = []
        
        # 解析指令名稱
        command_match = self.COMMAND_PATTERN.match(input_str)
        if not command_match:
            errors.append(ParseError(
                error_type=ParseErrorType.MISSING_COMMAND,
                message="指令必須以 / 開頭",
                position=0,
                suggestion="請使用格式: /command-name"
            ))
            return ParsedCommand(
                raw_input=input_str,
                command_name="",
                verb="",
                noun="",
                is_valid=False,
                errors=errors
            )
        
        command_name = command_match.group(1)
        
        # 分解動詞和名詞
        parts = command_name.split("-", 1)
        verb = parts[0]
        noun = parts[1] if len(parts) > 1 else ""
        
        # 解析輸入對象
        input_object = None
        input_match = self.INPUT_PATTERN.search(input_str)
        if input_match:
            input_object = InputObject(
                input_type=input_match.group(1),
                identifier=input_match.group(2),
                raw=input_match.group(0)
            )
        
        # 解析參數
        parameters: dict[str, Any] = {}
        
        # 先處理帶值參數
        for param_match in self.PARAM_PATTERN.finditer(input_str):
            key = param_match.group(1).replace("-", "_")
            value = self._parse_value(param_match.group(2))
            
            if key in parameters:
                errors.append(ParseError(
                    error_type=ParseErrorType.DUPLICATE_PARAMETER,
                    message=f"重複的參數: --{key}",
                    position=param_match.start()
                ))
            else:
                parameters[key] = value
        
        # 處理布林標記
        remaining = input_str
        for param_match in self.PARAM_PATTERN.finditer(input_str):
            remaining = remaining.replace(param_match.group(0), "")
        
        for flag_match in self.FLAG_PATTERN.finditer(remaining):
            key = flag_match.group(1).replace("-", "_")
            if key not in parameters:
                parameters[key] = True
        
        result = ParsedCommand(
            raw_input=input_str,
            command_name=command_name,
            verb=verb,
            noun=noun,
            input_object=input_object,
            parameters=parameters,
            is_valid=len(errors) == 0,
            errors=errors
        )
        
        self._cache[input_str] = result
        return result
    
    def _parse_value(self, value_str: str) -> str | int | float | bool:
        """
        解析參數值並轉換類型
        
        Args:
            value_str: 原始值字串
            
        Returns:
            轉換後的值
        """
        # 布林值
        if value_str.lower() in ("true", "yes", "on", "1"):
            return True
        if value_str.lower() in ("false", "no", "off", "0"):
            return False
        
        # 整數
        try:
            return int(value_str)
        except ValueError:
            pass
        
        # 浮點數
        try:
            return float(value_str)
        except ValueError:
            pass
        
        # 字串
        return value_str
    
    def clear_cache(self) -> None:
        """清除解析快取"""
        self._cache.clear()
    
    def validate_syntax(self, input_str: str) -> list[ParseError]:
        """
        驗證語法但不完整解析
        
        Args:
            input_str: 原始輸入字串
            
        Returns:
            錯誤列表（空列表表示語法正確）
        """
        result = self.parse(input_str)
        return result.errors


# 使用範例
if __name__ == "__main__":
    parser = CommandParser()
    
    # 測試解析
    test_cases = [
        "/analyze-data @file:sales.csv --format markdown",
        "/summarize-doc @url:https://example.com --length brief",
        "/convert-file @file:data.json --to csv --encoding utf-8",
        "/deploy-site @site:myapp --target production --backup",
        "/list-files --sort date",
        "invalid command",  # 錯誤測試
    ]
    
    for test in test_cases:
        result = parser.parse(test)
        print(f"\n輸入: {test}")
        print(f"有效: {result.is_valid}")
        if result.is_valid:
            print(f"指令: {result.command_name}")
            print(f"動詞: {result.verb}")
            print(f"名詞: {result.noun}")
            if result.input_object:
                print(f"輸入: {result.input_object}")
            if result.parameters:
                print(f"參數: {result.parameters}")
        else:
            for error in result.errors:
                print(f"錯誤: {error.message}")
