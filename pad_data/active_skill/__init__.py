import dataclasses
from typing import List

from pad_data.skill import SkillEffectTag

from . import effect

def post_process(effects: List[SkillEffectTag]) -> None:
    # merge repeated attacks into one instance
    for i, e in enumerate(effects):
        if isinstance(e, effect.AtkNuke):
            j = i + 1
            while j < len(effects) and e == effects[j]:
                j += 1
            if j - i == 1:
                continue
            merged_effect = dataclasses.replace(effects[i], repeat=j - i)
            effects[i:j] = [merged_effect]
            break

    for i, e in enumerate(effects):
        if isinstance(e, effect.MultiEffect):
            effects[i:i + 1] = e.items
