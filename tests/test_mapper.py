"""
Tests for Verb Mapper
"""

import pytest
from src.mapping.verb_mapper import VerbMapper, MappingResult
from src.mapping.synonyms import SynonymStore, create_default_store
from src.mapping.weights import WeightCalculator


class TestVerbMapper:
    """測試動詞映射器"""
    
    @pytest.fixture
    def mapper(self) -> VerbMapper:
        mapper = VerbMapper()
        # 註冊測試同義詞
        mapper.register_synonym("analyze-data", "analyze", 100)
        mapper.register_synonym("analyze-data", "inspect", 95)
        mapper.register_synonym("analyze-data", "examine", 92)
        mapper.register_synonym("summarize-doc", "summarize", 100)
        mapper.register_synonym("summarize-doc", "digest", 95)
        return mapper
    
    def test_exact_match(self, mapper: VerbMapper) -> None:
        """測試精確匹配"""
        result = mapper.map("analyze")
        
        assert result.matched
        assert result.target_command == "analyze-data"
        assert result.confidence == 100.0
        assert not result.requires_sabe
    
    def test_synonym_match(self, mapper: VerbMapper) -> None:
        """測試同義詞匹配"""
        result = mapper.map("inspect")
        
        assert result.matched
        assert result.target_command == "analyze-data"
        assert result.confidence == 95.0
    
    def test_high_confidence_no_sabe(self, mapper: VerbMapper) -> None:
        """測試高置信度不觸發 S.A.B.E."""
        result = mapper.map("examine")
        
        assert result.matched
        assert result.confidence >= 90.0
        assert not result.requires_sabe
    
    def test_no_match(self, mapper: VerbMapper) -> None:
        """測試無匹配"""
        result = mapper.map("unknownverb")
        
        assert not result.matched
        assert result.target_command is None
        assert result.requires_sabe
    
    def test_alternatives(self, mapper: VerbMapper) -> None:
        """測試備選項"""
        # 添加更多同義詞使得有多個候選
        mapper.register_synonym("convert-file", "transform", 90)
        
        result = mapper.map("inspect")
        
        # 應該有備選項
        assert isinstance(result.alternatives, list)


class TestSynonymStore:
    """測試同義詞庫"""
    
    def test_register_and_get(self) -> None:
        """測試註冊和取得"""
        store = SynonymStore()
        store.register("test-cmd", {"test": 100, "try": 90})
        
        synonyms = store.get("test-cmd")
        
        assert synonyms is not None
        assert synonyms["test"] == 100
        assert synonyms["try"] == 90
    
    def test_add_synonym(self) -> None:
        """測試添加單個同義詞"""
        store = SynonymStore()
        store.add_synonym("test-cmd", "test", 100)
        store.add_synonym("test-cmd", "try", 90)
        
        synonyms = store.get("test-cmd")
        
        assert len(synonyms) == 2
    
    def test_find_by_synonym(self) -> None:
        """測試根據同義詞查找"""
        store = SynonymStore()
        store.register("cmd1", {"test": 100})
        store.register("cmd2", {"test": 80})
        
        results = store.find_by_synonym("test")
        
        assert len(results) == 2
        assert results[0][0] == "cmd1"  # 權重較高的排前面
        assert results[0][1] == 100
    
    def test_remove_synonym(self) -> None:
        """測試移除同義詞"""
        store = SynonymStore()
        store.register("test-cmd", {"test": 100, "try": 90})
        
        result = store.remove_synonym("test-cmd", "try")
        
        assert result is True
        synonyms = store.get("test-cmd")
        assert "try" not in synonyms
    
    def test_create_default_store(self) -> None:
        """測試建立預設同義詞庫"""
        store = create_default_store()
        
        assert len(store) > 0
        assert "analyze-data" in store
        assert "summarize-doc" in store


class TestWeightCalculator:
    """測試權重計算器"""
    
    @pytest.fixture
    def calc(self) -> WeightCalculator:
        return WeightCalculator()
    
    def test_exact_match(self, calc: WeightCalculator) -> None:
        """測試精確匹配"""
        synonyms = {"analyze": 100, "inspect": 95}
        
        weight = calc.calculate("analyze", synonyms)
        
        assert weight == 100.0
    
    def test_synonym_match(self, calc: WeightCalculator) -> None:
        """測試同義詞匹配"""
        synonyms = {"analyze": 100, "inspect": 95}
        
        weight = calc.calculate("inspect", synonyms)
        
        assert weight == 95.0
    
    def test_no_match(self, calc: WeightCalculator) -> None:
        """測試無匹配"""
        synonyms = {"analyze": 100}
        
        weight = calc.calculate("unknown", synonyms)
        
        assert weight < 50  # 模糊匹配可能有低分
    
    def test_fuzzy_match_prefix(self, calc: WeightCalculator) -> None:
        """測試前綴模糊匹配"""
        synonyms = {"analyze": 100}
        
        weight = calc.calculate("anal", synonyms)
        
        assert weight > 0  # 應該有部分匹配分數
        assert weight < 100  # 但不應該是滿分
    
    def test_levenshtein_distance(self, calc: WeightCalculator) -> None:
        """測試編輯距離計算"""
        distance = calc._levenshtein_distance("kitten", "sitting")
        
        assert distance == 3
    
    def test_calculate_multi(self, calc: WeightCalculator) -> None:
        """測試多指令權重計算"""
        command_synonyms = {
            "analyze-data": {"analyze": 100, "inspect": 95},
            "summarize-doc": {"summarize": 100},
        }
        
        results = calc.calculate_multi("analyze", command_synonyms)
        
        assert len(results) >= 1
        assert results[0][0] == "analyze-data"
        assert results[0][1] == 100.0
