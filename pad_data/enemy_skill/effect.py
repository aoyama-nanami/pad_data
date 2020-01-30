from dataclasses import dataclass
from typing import List

from pad_data.common import Orb, Type
from pad_data.skill import skill_effect

@skill_effect
@dataclass
class BaseBuff:
    duration: int

@skill_effect
@dataclass
class VoidDamageShield(BaseBuff):
    threshold: int

@skill_effect
@dataclass
class ElementDamageReduction:
    elements: List[Orb]
    dr: int

@skill_effect
@dataclass
class TypeDamageReduction:
    types: List[Type]
    dr: int

@skill_effect
@dataclass
class SkillSetES:
    skill_ids: List[int]
