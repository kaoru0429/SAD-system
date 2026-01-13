"""
Mapping Package - 寬容映射引擎
"""

from .verb_mapper import VerbMapper
from .synonyms import SynonymStore
from .weights import WeightCalculator

__all__ = ["VerbMapper", "SynonymStore", "WeightCalculator"]
