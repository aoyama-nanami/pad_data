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

def board7x6(c):
    return any(isinstance(e, ls_effect.Board7x6) for e in c.leader_skill.effects)

# pylint: disable=undefined-variable
def main():
    db = database.Database()
    cards = db.get_all_released_cards()

    # cards = list(filter(lambda c: ehp(c) >= 1.5 and board7x6(c), cards))

    # cards = list(filter(filters.Skill(as_effect.AtkNuke, '_.value >= 100000'), cards))
    cards = list(filter(
        lambda c: (
            filters.LeaderSkill(ls_effect.ExtraBuff,
                                '_.move_time_extend >= 200')(c)
            and atk(c) >= 10), cards))

    # cards = list(filter(
    #     filters.Skill(
    #         effect.AllOrbChange,
    #         '_.orbs.count(FIRE) and _.orbs.count(LIGHT) and '
    #         'len(_.orbs) <= 4'),
    #     cards))
    for c in cards:
        c.dump(print_leader_skill=1, print_active_skill=0)

if __name__ == '__main__':
    main()
