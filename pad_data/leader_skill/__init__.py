import dataclasses
from typing import List

from pad_data.skill import SkillEffectTag

from . import effect

def post_process(effects: List[SkillEffectTag]) -> List[SkillEffectTag]:
    out: List[SkillEffectTag] = []
    cross: List[effect.CrossAtkBoost] = []
    heart_cross: List[effect.HeartCross] = []
    for e in effects:
        if isinstance(e, effect.MultiEffect):
            out += e.items
        elif isinstance(e, effect.CrossAtkBoost):
            cross.append(e)
        elif isinstance(e, effect.HeartCross):
            heart_cross.append(e)
        else:
            out.append(e)

    if len(cross) >= 2:
        merged = effect.CrossAtkBoost(args=[])
        for e in cross:
            for (i, a) in enumerate(e.atk_table):
                if not a:
                    continue
                assert merged.atk_table[i] == 0
                merged.atk_table[i] = a
        out.append(merged)
    else:
        out += cross

    if len(heart_cross) >= 2:
        merged_hc = heart_cross[0]
        for e in heart_cross[1:]:
            for field in dataclasses.fields(e):
                if field.name == 'dr':
                    if e.dr != 0:
                        assert merged_hc.dr == 0
                        merged_hc.dr = e.dr
                        merged_hc.dr_elements = e.dr_elements
                elif field.name == 'dr_elements':
                    pass
                elif field.type == int:
                    v = getattr(e, field.name)
                    if v != 0:
                        assert getattr(merged_hc, field.name) == 0
                        setattr(merged_hc, field.name, v)
                else:
                    assert (getattr(merged_hc, field.name) ==
                            getattr(e, field.name))
        out.append(merged_hc)
    else:
        out += heart_cross

    return out
