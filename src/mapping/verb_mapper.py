"""
Verb Mapper - 動詞映射模組

實現用字寬容的動詞智能映射
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .synonyms import SynonymStore
from .weights import WeightCalculator


@dataclass
class MappingResult:
    """映射結果"""
    input_verb: str
    matched: bool
    target_command: str | None
    confidence: float
    alternatives: list[dict[str, Any]]
    requires_sabe: bool
    
    @classmethod
    def no_match(cls, input_verb: str) -> MappingResult:
        """建立無匹配結果"""
        return cls(
            input_verb=input_verb,
            matched=False,
            target_command=None,
            confidence=0.0,
            alternatives=[],
            requires_sabe=True
        )


class VerbMapper:
    """
    動詞映射器
    
    實現「用字寬容」原則，將各種動詞變體映射到標準指令
    
    Example:
        >>> mapper = VerbMapper()
        >>> result = mapper.map("inspect")
        >>> print(result.target_command)
        'analyze-data'
    """
    
    def __init__(
        self,
        config_path: str | Path | None = None,
        direct_threshold: float = 90.0,
        reject_threshold: float = 30.0
    ) -> None:
        """
        初始化動詞映射器
        
        Args:
            config_path: 同義詞配置檔路徑
            direct_threshold: 直接映射閾值
            reject_threshold: 拒絕閾值
        """
        self.direct_threshold = direct_threshold
        self.reject_threshold = reject_threshold
        
        self._synonym_store = SynonymStore()
        self._weight_calculator = WeightCalculator()
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str | Path) -> None:
        """
        載入同義詞配置
        
        Args:
            config_path: 配置檔路徑
        """
        config_path = Path(config_path)
        if not config_path.exists():
            return
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        for command_name, command_config in config.items():
            synonyms = command_config.get("synonyms", {})
            self._synonym_store.register(command_name, synonyms)
    
    def map(self, verb: str, noun: str | None = None) -> MappingResult:
        """
        映射動詞到標準指令
        
        Args:
            verb: 輸入動詞
            noun: 可選的名詞部分
            
        Returns:
            映射結果
        """
        verb = verb.lower().strip()
        
        # 查找所有可能的匹配
        candidates = self._find_candidates(verb, noun)
        
        if not candidates:
            return MappingResult.no_match(verb)
        
        # 按置信度排序
        candidates.sort(key=lambda c: c["confidence"], reverse=True)
        best = candidates[0]
        
        # 判斷是否需要觸發 S.A.B.E.
        requires_sabe = best["confidence"] < self.direct_threshold
        
        return MappingResult(
            input_verb=verb,
            matched=True,
            target_command=best["command"],
            confidence=best["confidence"],
            alternatives=candidates[1:5],
            requires_sabe=requires_sabe
        )
    
    def _find_candidates(
        self,
        verb: str,
        noun: str | None
    ) -> list[dict[str, Any]]:
        """
        查找所有候選映射
        
        Args:
            verb: 動詞
            noun: 名詞
            
        Returns:
            候選列表
        """
        candidates: list[dict[str, Any]] = []
        
        # 遍歷所有註冊的指令
        for command_name, synonyms in self._synonym_store.items():
            # 計算動詞匹配度
            confidence = self._weight_calculator.calculate(verb, synonyms)
            
            if confidence >= self.reject_threshold:
                # 如果提供了名詞，進一步驗證
                if noun:
                    command_noun = command_name.split("-", 1)[-1] if "-" in command_name else ""
                    if command_noun and noun != command_noun:
                        # 名詞不匹配，降低置信度
                        confidence *= 0.7
                
                candidates.append({
                    "command": command_name,
                    "confidence": confidence,
                    "description": self._get_command_description(command_name)
                })
        
        return candidates
    
    def _get_command_description(self, command_name: str) -> str:
        """取得指令描述"""
        descriptions = {
            "analyze-data": "對數據進行詳細分析",
            "summarize-doc": "生成文件摘要",
            "convert-file": "轉換檔案格式",
            "generate-site": "生成靜態網站",
            "deploy-site": "部署網站",
            "delete-file": "刪除檔案",
            "list-files": "列出檔案",
            "search-content": "搜尋內容",
        }
        return descriptions.get(command_name, "")
    
    def register_synonym(
        self,
        command: str,
        synonym: str,
        weight: float = 80.0
    ) -> None:
        """
        註冊新的同義詞
        
        Args:
            command: 標準指令名稱
            synonym: 同義詞
            weight: 權重 (0-100)
        """
        self._synonym_store.add_synonym(command, synonym, weight)
    
    def get_all_synonyms(self, command: str) -> dict[str, float]:
        """
        取得指令的所有同義詞
        
        Args:
            command: 指令名稱
            
        Returns:
            同義詞及其權重
        """
        return self._synonym_store.get(command) or {}


# 測試
if __name__ == "__main__":
    mapper = VerbMapper()
    
    # 手動註冊一些同義詞進行測試
    mapper.register_synonym("analyze-data", "analyze", 100)
    mapper.register_synonym("analyze-data", "inspect", 95)
    mapper.register_synonym("analyze-data", "examine", 92)
    mapper.register_synonym("analyze-data", "investigate", 90)
    mapper.register_synonym("analyze-data", "look", 60)
    
    mapper.register_synonym("summarize-doc", "summarize", 100)
    mapper.register_synonym("summarize-doc", "digest", 95)
    mapper.register_synonym("summarize-doc", "condense", 92)
    
    # 測試映射
    test_verbs = ["analyze", "inspect", "look", "figure-out", "examine"]
    
    for verb in test_verbs:
        result = mapper.map(verb)
        print(f"\n動詞: {verb}")
        print(f"匹配: {result.matched}")
        print(f"目標: {result.target_command}")
        print(f"置信度: {result.confidence:.1f}%")
        print(f"需要 S.A.B.E.: {result.requires_sabe}")
        if result.alternatives:
            print(f"備選: {[a['command'] for a in result.alternatives]}")
