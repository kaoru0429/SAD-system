"""
Input Validator - 輸入驗證器

驗證指令輸入的有效性
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .parser import ParsedCommand, InputObject


class ValidationErrorType(Enum):
    """驗證錯誤類型"""
    MISSING_INPUT = "missing_input"
    INVALID_INPUT_TYPE = "invalid_input_type"
    INVALID_IDENTIFIER = "invalid_identifier"
    MISSING_REQUIRED_PARAM = "missing_required_param"
    INVALID_PARAM_VALUE = "invalid_param_value"
    UNKNOWN_PARAM = "unknown_param"


@dataclass
class ValidationError:
    """驗證錯誤"""
    error_type: ValidationErrorType
    message: str
    field: str | None = None
    suggestion: str | None = None


@dataclass
class ValidationResult:
    """驗證結果"""
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[str]
    
    @classmethod
    def success(cls) -> ValidationResult:
        """建立成功結果"""
        return cls(is_valid=True, errors=[], warnings=[])
    
    @classmethod
    def failure(cls, errors: list[ValidationError]) -> ValidationResult:
        """建立失敗結果"""
        return cls(is_valid=False, errors=errors, warnings=[])


class InputValidator:
    """
    輸入驗證器
    
    驗證解析後的指令輸入是否有效
    
    Example:
        >>> validator = InputValidator()
        >>> result = validator.validate(parsed_command, command_spec)
    """
    
    # 支援的輸入類型
    SUPPORTED_INPUT_TYPES = {
        "file": r"^[\w\-./\\]+$",
        "url": r"^https?://",
        "data": r"^[\w\-:]+$",
        "text": r".+",
        "directory": r"^[\w\-./\\]+$",
        "workspace": r"^[\w\-]+$",
        "site": r"^[\w\-]+$",
        "resource": r"^[\w\-:]+$",
        "conversation": r"^(latest|[\w\-]+)$",
    }
    
    def __init__(self) -> None:
        import re
        self._type_patterns = {
            k: re.compile(v) for k, v in self.SUPPORTED_INPUT_TYPES.items()
        }
    
    def validate(
        self,
        command: ParsedCommand,
        spec: Any | None = None  # CommandSpec
    ) -> ValidationResult:
        """
        驗證指令輸入
        
        Args:
            command: 解析後的指令
            spec: 指令規格（可選）
            
        Returns:
            驗證結果
        """
        errors: list[ValidationError] = []
        warnings: list[str] = []
        
        # 驗證輸入對象
        if command.input_object:
            input_errors = self._validate_input_object(command.input_object, spec)
            errors.extend(input_errors)
        elif spec and spec.input_types:
            # 指令需要輸入但未提供
            warnings.append(f"此指令支援輸入類型: {', '.join(spec.input_types)}")
        
        # 驗證參數
        if spec:
            param_errors = self._validate_parameters(command.parameters, spec)
            errors.extend(param_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_input_object(
        self,
        input_obj: InputObject,
        spec: Any | None
    ) -> list[ValidationError]:
        """
        驗證輸入對象
        
        Args:
            input_obj: 輸入對象
            spec: 指令規格
            
        Returns:
            錯誤列表
        """
        errors: list[ValidationError] = []
        
        # 檢查輸入類型是否支援
        if input_obj.input_type not in self.SUPPORTED_INPUT_TYPES:
            errors.append(ValidationError(
                error_type=ValidationErrorType.INVALID_INPUT_TYPE,
                message=f"不支援的輸入類型: {input_obj.input_type}",
                field="input_type",
                suggestion=f"支援的類型: {', '.join(self.SUPPORTED_INPUT_TYPES.keys())}"
            ))
            return errors
        
        # 檢查指令是否接受此輸入類型
        if spec and spec.input_types:
            if input_obj.input_type not in spec.input_types:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.INVALID_INPUT_TYPE,
                    message=f"此指令不接受 @{input_obj.input_type} 類型輸入",
                    field="input_type",
                    suggestion=f"請使用: {', '.join('@' + t for t in spec.input_types)}"
                ))
        
        # 驗證識別符格式
        pattern = self._type_patterns.get(input_obj.input_type)
        if pattern and not pattern.match(input_obj.identifier):
            errors.append(ValidationError(
                error_type=ValidationErrorType.INVALID_IDENTIFIER,
                message=f"無效的識別符格式: {input_obj.identifier}",
                field="identifier"
            ))
        
        return errors
    
    def _validate_parameters(
        self,
        parameters: dict[str, Any],
        spec: Any  # CommandSpec
    ) -> list[ValidationError]:
        """
        驗證參數
        
        Args:
            parameters: 參數字典
            spec: 指令規格
            
        Returns:
            錯誤列表
        """
        errors: list[ValidationError] = []
        
        # 建立參數規格映射
        param_specs = {p.name: p for p in spec.parameters}
        
        # 檢查必填參數
        for param_spec in spec.parameters:
            if param_spec.required and param_spec.name not in parameters:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.MISSING_REQUIRED_PARAM,
                    message=f"缺少必填參數: --{param_spec.name}",
                    field=param_spec.name,
                    suggestion=param_spec.description
                ))
        
        # 驗證參數值
        for key, value in parameters.items():
            param_key = key.replace("_", "-")  # 還原原始格式
            
            if param_key in param_specs:
                param_spec = param_specs[param_key]
                
                # 檢查選項限制
                if param_spec.choices and str(value) not in param_spec.choices:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.INVALID_PARAM_VALUE,
                        message=f"無效的參數值: --{param_key} {value}",
                        field=param_key,
                        suggestion=f"可用值: {', '.join(param_spec.choices)}"
                    ))
        
        return errors
    
    def validate_input_exists(
        self,
        input_obj: InputObject,
        context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """
        驗證輸入對象是否實際存在
        
        Args:
            input_obj: 輸入對象
            context: 上下文資訊（如檔案系統、資料庫等）
            
        Returns:
            驗證結果
        """
        # 這是一個需要外部依賴的驗證
        # 目前只做格式驗證，實際存在性驗證需要整合外部服務
        
        errors: list[ValidationError] = []
        
        # 基本格式驗證
        if not input_obj.identifier:
            errors.append(ValidationError(
                error_type=ValidationErrorType.INVALID_IDENTIFIER,
                message="輸入識別符不能為空",
                field="identifier"
            ))
        
        # TODO: 實際存在性驗證
        # - file: 檢查檔案是否存在
        # - url: 檢查 URL 是否可達
        # - data: 檢查資料 ID 是否存在
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=[]
        )


# 測試
if __name__ == "__main__":
    from .parser import CommandParser
    
    parser = CommandParser()
    validator = InputValidator()
    
    # 測試驗證
    cmd = parser.parse("/analyze-data @file:test.csv --format markdown")
    result = validator.validate(cmd)
    
    print(f"有效: {result.is_valid}")
    if result.errors:
        for error in result.errors:
            print(f"錯誤: {error.message}")
    if result.warnings:
        for warning in result.warnings:
            print(f"警告: {warning}")
