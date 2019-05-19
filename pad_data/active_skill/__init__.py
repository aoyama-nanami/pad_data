import dataclasses

from . import effect

def post_process(effects):
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

    # DoubleOrbChange -> OrbChange * 2
    for i, e in enumerate(effects):
        if isinstance(e, effect.DoubleOrbChange):
            effects[i:i + 1] = [
                effect.OrbChange([e.from1], [e.to1]),
                effect.OrbChange([e.from2], [e.to2]),
            ]
            break
