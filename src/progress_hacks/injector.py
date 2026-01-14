"""
Hack Injector - 技巧注入器

Injects prompt hacks into prompts with optional effects.
將提示技巧注入到提示中，可選擇效果。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .hacks import PromptHack


class InjectionStyle(Enum):
    """注入樣式 | Injection Style"""
    MINIMAL = "minimal"       # Just the postscript | 僅附言
    DEFAULT = "default"       # With header | 帶標題
    BOXED = "boxed"           # In a box | 框線樣式
    HIGHLIGHT = "highlight"   # Highlighted | 高亮樣式


class InjectionPosition(Enum):
    """注入位置 | Injection Position"""
    PREPEND = "prepend"       # At the beginning | 在開頭
    APPEND = "append"         # At the end | 在結尾
    WRAP = "wrap"             # Wrap the prompt | 包裹提示


@dataclass
class InjectionResult:
    """
    Injection result container.
    注入結果容器。
    """
    original_prompt: str
    injected_prompt: str
    hack: PromptHack
    style: InjectionStyle
    position: InjectionPosition
    
    @property
    def was_modified(self) -> bool:
        """Check if prompt was modified."""
        return self.original_prompt != self.injected_prompt


class HackInjector:
    """
    技巧注入器 | Hack Injector
    
    Injects prompt hacks into prompts with configurable styling.
    將提示技巧注入到提示中，可配置樣式。
    
    Example:
        >>> injector = HackInjector()
        >>> result = injector.inject(prompt, hack)
        >>> print(result.injected_prompt)
    """
    
    def __init__(
        self,
        default_style: InjectionStyle = InjectionStyle.DEFAULT,
        default_position: InjectionPosition = InjectionPosition.APPEND,
        on_inject: Callable[[PromptHack], None] | None = None
    ) -> None:
        """
        Initialize hack injector.
        初始化技巧注入器。
        
        Args:
            default_style: Default injection style | 預設注入樣式
            default_position: Default injection position | 預設注入位置
            on_inject: Callback after injection | 注入後的回調
        """
        self._default_style = default_style
        self._default_position = default_position
        self._on_inject = on_inject
    
    def inject(
        self,
        prompt: str,
        hack: PromptHack,
        style: InjectionStyle | None = None,
        position: InjectionPosition | None = None,
        enhanced: bool = False
    ) -> InjectionResult:
        """
        Inject a hack into a prompt.
        將技巧注入到提示中。
        
        Args:
            prompt: Original prompt | 原始提示
            hack: PromptHack to inject | 要注入的技巧
            style: Injection style | 注入樣式
            position: Injection position | 注入位置
            enhanced: Use enhanced version | 使用增強版本
            
        Returns:
            InjectionResult with modified prompt | 包含修改後提示的注入結果
        """
        style = style or self._default_style
        position = position or self._default_position
        
        # Format the hack
        formatted_hack = self._format_hack(hack, style, enhanced)
        
        # Inject based on position
        if position == InjectionPosition.PREPEND:
            injected = f"{formatted_hack}\n\n{prompt}"
        elif position == InjectionPosition.APPEND:
            injected = f"{prompt}\n\n{formatted_hack}"
        else:  # WRAP
            injected = f"{formatted_hack}\n\n{prompt}\n\n{formatted_hack}"
        
        # Callback
        if self._on_inject:
            self._on_inject(hack)
        
        return InjectionResult(
            original_prompt=prompt,
            injected_prompt=injected,
            hack=hack,
            style=style,
            position=position
        )
    
    def _format_hack(
        self,
        hack: PromptHack,
        style: InjectionStyle,
        enhanced: bool = False
    ) -> str:
        """Format hack for injection."""
        postscript = hack.get_postscript(enhanced=enhanced)
        
        if style == InjectionStyle.MINIMAL:
            return postscript
        
        if style == InjectionStyle.BOXED:
            return self._format_boxed(hack, postscript)
        
        if style == InjectionStyle.HIGHLIGHT:
            return self._format_highlighted(hack, postscript)
        
        # Default
        return self._format_default(hack, postscript)
    
    def _format_default(self, hack: PromptHack, postscript: str) -> str:
        """Default formatting with header."""
        return f"""
─────────────────────────────────────────
{hack.display_name}
─────────────────────────────────────────
{postscript}
─────────────────────────────────────────
"""
    
    def _format_boxed(self, hack: PromptHack, postscript: str) -> str:
        """Boxed formatting."""
        width = 55
        title = hack.display_name
        
        lines = [
            "╭" + "─" * width + "╮",
            f"│ {title:^{width-2}} │",
            "├" + "─" * width + "┤",
        ]
        
        # Wrap postscript lines
        for line in postscript.split('\n'):
            while len(line) > width - 4:
                lines.append(f"│ {line[:width-4]} │")
                line = line[width-4:]
            lines.append(f"│ {line:<{width-4}} │")
        
        lines.append("╰" + "─" * width + "╯")
        
        return '\n'.join(lines)
    
    def _format_highlighted(self, hack: PromptHack, postscript: str) -> str:
        """Highlighted formatting with emphasis."""
        return f"""
▶▶▶ {hack.display_name} ◀◀◀

>>> {postscript}

▶▶▶ End of {hack.name_en} Hack ◀◀◀
"""
    
    def format_notification(self, hack: PromptHack) -> str:
        """
        Format a notification that hack was injected.
        格式化技巧已注入的通知。
        
        Args:
            hack: The injected hack | 已注入的技巧
            
        Returns:
            Notification string | 通知字串
        """
        return f"""
┌─────────────────────────────────────────┐
│ ✨ {hack.display_name} 已注入           │
│    {hack.name_en} Hack Injected         │
└─────────────────────────────────────────┘
"""
    
    def format_preview(self, hack: PromptHack) -> str:
        """
        Format a preview of the hack.
        格式化技巧的預覽。
        
        Args:
            hack: Hack to preview | 要預覽的技巧
            
        Returns:
            Preview string | 預覽字串
        """
        use_when = '\n'.join(f"  • {u}" for u in hack.use_when)
        
        return f"""
{hack.display_name}
{'─' * 50}

📋 Postscript | 附言:
{hack.postscript}

📌 Use when | 適用場景:
{use_when}
"""


def create_injector(
    style: str = "default",
    position: str = "append"
) -> HackInjector:
    """
    Factory function to create a HackInjector.
    建立 HackInjector 的工廠函數。
    
    Args:
        style: Style name | 樣式名稱
        position: Position name | 位置名稱
        
    Returns:
        Configured HackInjector | 已配置的 HackInjector
    """
    style_map = {
        "minimal": InjectionStyle.MINIMAL,
        "default": InjectionStyle.DEFAULT,
        "boxed": InjectionStyle.BOXED,
        "highlight": InjectionStyle.HIGHLIGHT,
    }
    
    position_map = {
        "prepend": InjectionPosition.PREPEND,
        "append": InjectionPosition.APPEND,
        "wrap": InjectionPosition.WRAP,
    }
    
    return HackInjector(
        default_style=style_map.get(style, InjectionStyle.DEFAULT),
        default_position=position_map.get(position, InjectionPosition.APPEND)
    )
