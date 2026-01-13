"""
Synonym Store - 同義詞庫

管理指令與同義詞的映射關係
"""

from __future__ import annotations

from typing import Iterator


class SynonymStore:
    """
    同義詞庫
    
    儲存和管理指令的同義詞及其權重
    
    Example:
        >>> store = SynonymStore()
        >>> store.register("analyze-data", {"analyze": 100, "inspect": 95})
        >>> synonyms = store.get("analyze-data")
    """
    
    def __init__(self) -> None:
        self._store: dict[str, dict[str, float]] = {}
    
    def register(
        self,
        command: str,
        synonyms: dict[str, float]
    ) -> None:
        """
        註冊指令的同義詞
        
        Args:
            command: 指令名稱
            synonyms: 同義詞字典 {同義詞: 權重}
        """
        if command not in self._store:
            self._store[command] = {}
        
        self._store[command].update(synonyms)
    
    def add_synonym(
        self,
        command: str,
        synonym: str,
        weight: float
    ) -> None:
        """
        添加單個同義詞
        
        Args:
            command: 指令名稱
            synonym: 同義詞
            weight: 權重 (0-100)
        """
        if command not in self._store:
            self._store[command] = {}
        
        self._store[command][synonym] = min(max(weight, 0), 100)
    
    def remove_synonym(self, command: str, synonym: str) -> bool:
        """
        移除同義詞
        
        Args:
            command: 指令名稱
            synonym: 同義詞
            
        Returns:
            是否成功移除
        """
        if command in self._store and synonym in self._store[command]:
            del self._store[command][synonym]
            return True
        return False
    
    def get(self, command: str) -> dict[str, float] | None:
        """
        取得指令的所有同義詞
        
        Args:
            command: 指令名稱
            
        Returns:
            同義詞字典或 None
        """
        return self._store.get(command)
    
    def find_by_synonym(self, synonym: str) -> list[tuple[str, float]]:
        """
        根據同義詞查找指令
        
        Args:
            synonym: 同義詞
            
        Returns:
            匹配的 (指令, 權重) 列表
        """
        results: list[tuple[str, float]] = []
        
        for command, synonyms in self._store.items():
            if synonym in synonyms:
                results.append((command, synonyms[synonym]))
        
        # 按權重排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def items(self) -> Iterator[tuple[str, dict[str, float]]]:
        """迭代所有指令及其同義詞"""
        return iter(self._store.items())
    
    def commands(self) -> list[str]:
        """取得所有指令名稱"""
        return list(self._store.keys())
    
    def clear(self) -> None:
        """清空同義詞庫"""
        self._store.clear()
    
    def __len__(self) -> int:
        return len(self._store)
    
    def __contains__(self, command: str) -> bool:
        return command in self._store


# 預設同義詞庫
DEFAULT_SYNONYMS: dict[str, dict[str, float]] = {
    "analyze-data": {
        "analyze": 100,
        "inspect": 95,
        "examine": 92,
        "investigate": 90,
        "review": 85,
        "check": 80,
        "study": 78,
        "evaluate": 75,
    },
    "summarize-doc": {
        "summarize": 100,
        "digest": 95,
        "condense": 92,
        "brief": 90,
        "abstract": 88,
        "outline": 85,
        "recap": 82,
    },
    "convert-file": {
        "convert": 100,
        "transform": 95,
        "change": 88,
        "translate": 85,
        "switch": 80,
        "modify": 75,
    },
    "generate-site": {
        "generate": 100,
        "create": 98,
        "build": 95,
        "make": 90,
        "produce": 85,
        "construct": 82,
    },
    "deploy-site": {
        "deploy": 100,
        "publish": 95,
        "release": 92,
        "launch": 90,
    },
    "delete-file": {
        "delete": 100,
        "remove": 95,
        "erase": 92,
        "destroy": 90,
    },
    "list-files": {
        "list": 100,
        "show": 95,
        "display": 92,
        "enumerate": 88,
    },
    "search-content": {
        "search": 100,
        "find": 98,
        "locate": 95,
        "lookup": 92,
        "query": 88,
    },
}


def create_default_store() -> SynonymStore:
    """建立預設同義詞庫"""
    store = SynonymStore()
    for command, synonyms in DEFAULT_SYNONYMS.items():
        store.register(command, synonyms)
    return store
