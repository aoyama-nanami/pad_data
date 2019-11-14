from dataclasses import dataclass
from typing import List

from pad_data.common import Orb, Type

@dataclass
class BaseBuff:
    duration: int

@dataclass
class VoidDamageShield(BaseBuff):
    threshold: int

@dataclass
class ElementDamageReduction:
    elements: List[Orb]
    dr: int

@dataclass
class TypeDamageReduction:
    types: List[Type]
    dr: int

@dataclass
class SkillSetES:
    skill_ids: List[int]
