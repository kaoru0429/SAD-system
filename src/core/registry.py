"""
Command Registry - 指令註冊表

管理所有已註冊的指令，支援裝飾器註冊方式
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable

import yaml
from pathlib import Path


class RiskLevel(Enum):
    """風險等級"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Category(Enum):
    """指令類別"""
    DATA_ANALYSIS = "數據分析"
    FILE_OPERATION = "文件操作"
    WEB_DEPLOY = "網頁部署"
    SYSTEM = "系統操作"
    CUSTOM = "自定義"


@dataclass
class ParameterSpec:
    """參數規格"""
    name: str
    description: str
    required: bool = False
    default: Any = None
    choices: list[str] | None = None
    param_type: type = str


@dataclass
class CommandSpec:
    """指令規格"""
    name: str
    description: str
    handler: Callable[..., Any] | None = None
    category: Category = Category.CUSTOM
    risk_level: RiskLevel = RiskLevel.LOW
    synonyms: list[str] = field(default_factory=list)
    parameters: list[ParameterSpec] = field(default_factory=list)
    input_types: list[str] = field(default_factory=list)
    requires_confirmation: bool = False
    enabled: bool = True
    
    @property
    def verb(self) -> str:
        """取得動詞部分"""
        parts = self.name.split("-", 1)
        return parts[0]
    
    @property
    def noun(self) -> str:
        """取得名詞部分"""
        parts = self.name.split("-", 1)
        return parts[1] if len(parts) > 1 else ""


class CommandRegistry:
    """
    指令註冊表
    
    管理所有已註冊的指令，提供查找、驗證功能
    
    Example:
        >>> registry = CommandRegistry()
        >>> registry.register(CommandSpec(name="analyze-data", ...))
        >>> cmd = registry.get("analyze-data")
    """
    
    _instance: CommandRegistry | None = None
    
    def __new__(cls) -> CommandRegistry:
        """單例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._commands = {}
            cls._instance._verb_index = {}
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if not self._initialized:
            self._commands: dict[str, CommandSpec] = {}
            self._verb_index: dict[str, list[str]] = {}
            self._initialized = True
    
    def register(self, spec: CommandSpec) -> None:
        """
        註冊指令
        
        Args:
            spec: 指令規格
        """
        self._commands[spec.name] = spec
        
        # 建立動詞索引
        verb = spec.verb
        if verb not in self._verb_index:
            self._verb_index[verb] = []
        if spec.name not in self._verb_index[verb]:
            self._verb_index[verb].append(spec.name)
        
        # 同義詞索引
        for synonym in spec.synonyms:
            if synonym not in self._verb_index:
                self._verb_index[synonym] = []
            if spec.name not in self._verb_index[synonym]:
                self._verb_index[synonym].append(spec.name)
    
    def unregister(self, name: str) -> bool:
        """
        取消註冊指令
        
        Args:
            name: 指令名稱
            
        Returns:
            是否成功取消
        """
        if name in self._commands:
            spec = self._commands[name]
            del self._commands[name]
            
            # 清理動詞索引
            verb = spec.verb
            if verb in self._verb_index:
                self._verb_index[verb] = [
                    n for n in self._verb_index[verb] if n != name
                ]
            
            return True
        return False
    
    def get(self, name: str) -> CommandSpec | None:
        """
        取得指令規格
        
        Args:
            name: 指令名稱
            
        Returns:
            指令規格或 None
        """
        return self._commands.get(name)
    
    def find_by_verb(self, verb: str) -> list[CommandSpec]:
        """
        根據動詞查找指令
        
        Args:
            verb: 動詞
            
        Returns:
            匹配的指令列表
        """
        names = self._verb_index.get(verb, [])
        return [self._commands[name] for name in names if name in self._commands]
    
    def exists(self, name: str) -> bool:
        """
        檢查指令是否存在
        
        Args:
            name: 指令名稱
            
        Returns:
            是否存在
        """
        return name in self._commands
    
    def list_all(self) -> list[CommandSpec]:
        """
        列出所有指令
        
        Returns:
            所有指令規格列表
        """
        return list(self._commands.values())
    
    def list_by_category(self, category: Category) -> list[CommandSpec]:
        """
        根據類別列出指令
        
        Args:
            category: 指令類別
            
        Returns:
            指定類別的指令列表
        """
        return [
            spec for spec in self._commands.values()
            if spec.category == category
        ]
    
    def list_high_risk(self) -> list[CommandSpec]:
        """
        列出高風險指令
        
        Returns:
            高風險指令列表
        """
        return [
            spec for spec in self._commands.values()
            if spec.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
        ]
    
    def load_from_yaml(self, config_path: str | Path) -> int:
        """
        從 YAML 配置載入指令定義
        
        Args:
            config_path: 配置檔路徑
            
        Returns:
            載入的指令數量
        """
        config_path = Path(config_path)
        if not config_path.exists():
            return 0
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        count = 0
        commands = config.get("commands", {})
        
        for name, spec_dict in commands.items():
            parameters = []
            for param_name, param_config in spec_dict.get("parameters", {}).items():
                parameters.append(ParameterSpec(
                    name=param_name,
                    description=param_config.get("description", ""),
                    required=param_config.get("required", False),
                    default=param_config.get("default"),
                    choices=param_config.get("choices")
                ))
            
            risk_level_str = spec_dict.get("risk_level", "low")
            risk_level = RiskLevel(risk_level_str)
            
            spec = CommandSpec(
                name=name,
                description=spec_dict.get("description", ""),
                category=Category.CUSTOM,  # TODO: 從配置解析
                risk_level=risk_level,
                parameters=parameters,
                input_types=spec_dict.get("input_types", []),
                requires_confirmation=spec_dict.get("requires_confirmation", False)
            )
            
            self.register(spec)
            count += 1
        
        return count
    
    def clear(self) -> None:
        """清除所有註冊的指令"""
        self._commands.clear()
        self._verb_index.clear()


# 全域註冊表
_registry = CommandRegistry()


def register_command(
    name: str,
    description: str = "",
    synonyms: list[str] | None = None,
    category: Category = Category.CUSTOM,
    risk_level: RiskLevel = RiskLevel.LOW,
    parameters: list[ParameterSpec] | None = None,
    input_types: list[str] | None = None,
    requires_confirmation: bool = False
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    指令註冊裝飾器
    
    Args:
        name: 指令名稱
        description: 指令描述
        synonyms: 同義詞列表
        category: 指令類別
        risk_level: 風險等級
        parameters: 參數規格列表
        input_types: 支援的輸入類型
        requires_confirmation: 是否需要確認
        
    Returns:
        裝飾器函數
        
    Example:
        >>> @register_command(
        ...     name="analyze-data",
        ...     synonyms=["analyze", "inspect"],
        ...     category=Category.DATA_ANALYSIS
        ... )
        ... def analyze_data(input_obj, **params):
        ...     pass
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        spec = CommandSpec(
            name=name,
            description=description or func.__doc__ or "",
            handler=func,
            category=category,
            risk_level=risk_level,
            synonyms=synonyms or [],
            parameters=parameters or [],
            input_types=input_types or [],
            requires_confirmation=requires_confirmation
        )
        _registry.register(spec)
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
        
        wrapper._command_spec = spec  # type: ignore
        return wrapper
    
    return decorator


def get_registry() -> CommandRegistry:
    """取得全域註冊表"""
    return _registry


# 測試
if __name__ == "__main__":
    # 使用裝飾器註冊
    @register_command(
        name="test-command",
        description="測試指令",
        synonyms=["test", "try"],
        category=Category.CUSTOM,
        risk_level=RiskLevel.LOW
    )
    def test_command(input_obj: Any, **params: Any) -> str:
        return f"Executed with {input_obj} and {params}"
    
    # 查詢
    registry = get_registry()
    print(f"已註冊指令數: {len(registry.list_all())}")
    
    cmd = registry.get("test-command")
    if cmd:
        print(f"指令: {cmd.name}")
        print(f"描述: {cmd.description}")
        print(f"同義詞: {cmd.synonyms}")
