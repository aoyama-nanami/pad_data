#! /usr/bin/env python3

from pad_data import common, database, filters, util
from pad_data.active_skill import effect

util.import_enum_members(common.Awakening, globals())
util.import_enum_members(common.Orb, globals())
util.import_enum_members(common.Type, globals())

Type = common.Type
Orb = common.Orb
Awakening = common.Awakening

# pylint: disable=undefined-variable
def main():
    db = database.Database()
    cards = db.get_all_released_cards()

    cards = filter(lambda c: c.inheritable, cards)

    cards = list(filter(
        filters.Skill(effect.AtkNuke, '_.percentage[0] >= 25000'),
        cards))

    # cards = list(filter(
    #     filters.Skill(
    #         effect.AllOrbChange,
    #         '_.orbs.count(FIRE) and _.orbs.count(LIGHT) and '
    #         'len(_.orbs) <= 4'),
    #     cards))
    cards.sort(key=lambda c: c.skill.turn_min)
    for c in cards:
        c.dump()

if __name__ == '__main__':
    main()
