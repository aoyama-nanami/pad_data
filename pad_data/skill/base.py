from abc import ABC
import dataclasses
from typing import Any, List, Mapping, Optional, Tuple

class SkillEffectTag(ABC):
    pass

def skill_effect(cls: type) -> type:
    return SkillEffectTag.register(cls)

@dataclasses.dataclass
class Skill:
    name: str
    description: str
    effects: List[SkillEffectTag]
    turn_max: Optional[int]
    turn_min: Optional[int]

    @property
    def clean_description(self) -> str:
        return self.description.replace('\n', '')

    def effects_to_tuples(self) -> List[Tuple[str, Mapping[str, Any]]]:
        return [(type(e).__name__, e.__dict__) for e in self.effects]
