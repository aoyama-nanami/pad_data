#! /usr/bin/env python3

import path_common

from pad_data import common, database, filters, util
from pad_data.leader_skill import effect as ls_effect
from pad_data.active_skill import effect as as_effect

util.import_enum_members(common.Awakening, globals())
util.import_enum_members(common.Orb, globals())
util.import_enum_members(common.Type, globals())

Type = common.Type
Orb = common.Orb
Awakening = common.Awakening

def ehp(c):
    ret = 1
    for e in c.leader_skill.ls_effects:
        if not isinstance(e, ls_effect.BaseStatBoost):
            continue
        if isinstance(e, (ls_effect.HpAbove, ls_effect.HpBelow)):
            continue
        ret *= e.ls_effective_hp()
    return ret

def atk(c):
    ret = 1
    for e in c.leader_skill.effects:
        if not isinstance(e, ls_effect.BaseStatBoost):
            continue
        if isinstance(e, (ls_effect.HpAbove, ls_effect.HpBelow)):
            continue

        if isinstance(e, ls_effect.SteppedStatBoost) and e.atk_step > 0:
            ret *= (e.atk + e.max_step() * e.atk_step) / 100
        else:
            ret *= e.atk / 100
    return ret

def main():
    db = database.Database()
    cards = db.get_all_released_cards()

    filter_obj = (filters.Skill(as_effect.Heal, '_.hp_percentage >= 100') &
                  filters.INHERITABLE)

    cards = filter(filter_obj, cards)
    if filter_obj.is_active_skill:
        cards = sorted(cards, key=lambda c: c.skill.turn_min)
    else:
        cards = sorted(cards, key=atk)
    for c in cards:
        c.dump(print_leader_skill=not filter_obj.is_active_skill,
               print_active_skill=filter_obj.is_active_skill)

if __name__ == '__main__':
    main()
