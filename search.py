#! /usr/bin/env python3

from pad_data import common, database, effect, filters, util

util.import_enum_members(common.Awakening, globals())
util.import_enum_members(common.Orb, globals())
util.import_enum_members(common.Type, globals())

Type = common.Type
Orb = common.Orb
Awakening = common.Awakening
_ = filters.Placeholder()

# pylint: disable=undefined-variable
def main():
    db = database.Database()
    cards = db.get_all_released_cards()

    cards = filter(lambda c: c.inheritable, cards)

#    cards = list(filter(
#        filters.Skill(effect.AtkNuke, _.percentage[0] >= 25000),
#        cards))

    cards = list(filter(
        filters.Skill(
            effect.AllOrbChange,
            _.orbs.count(FIRE) & _.orbs.count(LIGHT) & (_.orbs.__len__() <= 4)),
        cards))
    cards.sort(key=lambda c: c.skill.turn_min)
    for c in cards:
        c.dump()

if __name__ == '__main__':
    main()
