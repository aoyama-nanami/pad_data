from . import effect

def post_process(effects):
    out = []
    cross = []
    for e in effects:
        if isinstance(e, list):
            out += e
        elif isinstance(e, effect.CrossAtkBoost):
            cross.append(e)
        else:
            out.append(e)
    if len(cross) >= 2:
        merged = effect.CrossAtkBoost([])
        for e in cross:
            for (i, a) in enumerate(e.atk_table):
                if not a:
                    continue
                if merged.atk_table[i] == 0:
                    merged.atk_table[i] = a
                else:
                    merged.atk_table[i] = merged.atk_table[i] * a / 100
        out.append(merged)
    else:
        out += cross
    return out
