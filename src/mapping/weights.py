"""
Weight Calculator - 權重計算器

計算動詞匹配的置信度權重
"""

from __future__ import annotations


class WeightCalculator:
    """
    權重計算器
    
    計算輸入動詞與目標動詞的匹配置信度
    
    Example:
        >>> calc = WeightCalculator()
        >>> weight = calc.calculate("inspect", {"analyze": 100, "inspect": 95})
        95.0
    """
    
    def __init__(self, fuzzy_match_enabled: bool = True) -> None:
        """
        初始化權重計算器
        
        Args:
            fuzzy_match_enabled: 是否啟用模糊匹配
        """
        self.fuzzy_match_enabled = fuzzy_match_enabled
    
    def calculate(
        self,
        input_verb: str,
        synonyms: dict[str, float]
    ) -> float:
        """
        計算匹配權重
        
        Args:
            input_verb: 輸入動詞
            synonyms: 同義詞字典 {同義詞: 權重}
            
        Returns:
            匹配權重 (0-100)
        """
        input_verb = input_verb.lower().strip()
        
        # 精確匹配
        if input_verb in synonyms:
            return synonyms[input_verb]
        
        # 模糊匹配
        if self.fuzzy_match_enabled:
            best_match = self._fuzzy_match(input_verb, synonyms)
            if best_match > 0:
                return best_match
        
        return 0.0
    
    def _fuzzy_match(
        self,
        input_verb: str,
        synonyms: dict[str, float]
    ) -> float:
        """
        模糊匹配
        
        Args:
            input_verb: 輸入動詞
            synonyms: 同義詞字典
            
        Returns:
            最佳匹配權重
        """
        best_weight = 0.0
        
        for synonym, weight in synonyms.items():
            # 前綴匹配
            if synonym.startswith(input_verb) or input_verb.startswith(synonym):
                # 根據匹配程度調整權重
                match_ratio = min(len(input_verb), len(synonym)) / max(len(input_verb), len(synonym))
                adjusted_weight = weight * match_ratio * 0.7  # 模糊匹配降權 30%
                best_weight = max(best_weight, adjusted_weight)
            
            # Levenshtein 距離匹配
            distance = self._levenshtein_distance(input_verb, synonym)
            max_len = max(len(input_verb), len(synonym))
            if max_len > 0:
                similarity = 1 - (distance / max_len)
                if similarity > 0.7:  # 相似度超過 70% 才考慮
                    adjusted_weight = weight * similarity * 0.6  # 距離匹配降權 40%
                    best_weight = max(best_weight, adjusted_weight)
        
        return best_weight
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        計算 Levenshtein 編輯距離
        
        Args:
            s1: 字串 1
            s2: 字串 2
            
        Returns:
            編輯距離
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def calculate_multi(
        self,
        input_verb: str,
        command_synonyms: dict[str, dict[str, float]]
    ) -> list[tuple[str, float]]:
        """
        對多個指令計算匹配權重
        
        Args:
            input_verb: 輸入動詞
            command_synonyms: {指令名: 同義詞字典}
            
        Returns:
            排序後的 (指令, 權重) 列表
        """
        results: list[tuple[str, float]] = []
        
        for command, synonyms in command_synonyms.items():
            weight = self.calculate(input_verb, synonyms)
            if weight > 0:
                results.append((command, weight))
        
        # 按權重降序排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results


# 測試
if __name__ == "__main__":
    calc = WeightCalculator()
    
    synonyms = {
        "analyze": 100,
        "inspect": 95,
        "examine": 92,
        "investigate": 90,
    }
    
    test_verbs = ["analyze", "inspect", "anal", "investig", "look", "analyz"]
    
    for verb in test_verbs:
        weight = calc.calculate(verb, synonyms)
        print(f"{verb}: {weight:.1f}")
