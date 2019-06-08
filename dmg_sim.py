#! /usr/bin/env python3

from dataclasses import dataclass
import itertools
import math
from typing import List, Optional
import wcwidth

from pad_data import database, util
from pad_data.common import Awakening, Combo, Orb, Shape, Type
from pad_data.leader_skill import effect as LS

util.import_enum_members(Awakening, globals())
util.import_enum_members(Orb, globals())
util.import_enum_members(Type, globals())

DB = database.Database()

@dataclass
class Team:
    card_id: int
    lv: int
    awakening_count: int = 9
    atk_plus: int = 99
    super_awakening: Optional[Awakening] = None

# pylint: disable=undefined-variable
TEAM = [
    Team(card_id=5331, lv=101, super_awakening=L_ATTACK),
    Team(card_id=5331, lv=110, super_awakening=L_ATTACK),
    Team(card_id=3713, lv=99),
    Team(card_id=5139, lv=101, super_awakening=BONUS_ATTACK),
    Team(card_id=4283, lv=99),
    Team(card_id=3885, lv=110, super_awakening=EXTEND_TIME_PLUS),
]
ASSIST = [
    None,
    Team(card_id=5190, lv=1, atk_plus=0),
    Team(card_id=4970, lv=1, atk_plus=0),
    None,
    None,
    None,
]
# pylint: disable=undefined-variable
COMBOS = [
    Combo(WOOD),
    Combo(FIRE),
    Combo(LIGHT),
    Combo(DARK, 5, Shape.L),
    Combo(LIGHT),
    Combo(WATER, 5, Shape.L),
    Combo(WATER, 4),
    Combo(WOOD, 5),
    Combo(WATER),
]
TRIGGER = False
HP = 100

@dataclass
class MemberSpec:
    name: str
    element: Orb
    sub_element: Optional[Orb]
    types: List[Type]
    atk: int
    awakenings: List[Awakening]

# pylint: disable=undefined-variable
def member_spec(base, assist):
    card = DB.card(base.card_id)
    atk = card.atk_at_level(base.lv) + base.atk_plus * 5
    assert base.awakening_count == 9
    awakenings = card.awakenings
    if base.super_awakening is not None:
        assert base.super_awakening in card.super_awakenings
        awakenings.append(base.super_awakening)
    if assist is not None:
        assert assist.awakening_count == 9
        assist_card = DB.card(assist.card_id)
        if AWOKEN_ASSIST in assist_card.awakenings:
            awakenings += assist_card.awakenings[1:]
        if card.element == assist_card.element:
            assist_atk = (assist_card.atk_at_level(assist.lv)
                          + assist_card.atk_plus * 5)
            atk += round(assist_atk * 0.05)

    atk += awakenings.count(ENHANCED_ATK) * 100
    atk -= awakenings.count(REDUCE_ATK) * 1000

    return MemberSpec(
        name=card.name,
        element=card.element,
        sub_element=card.sub_element,
        types=card.type,
        atk=atk,
        awakenings=awakenings
    )

# pylint: disable=undefined-variable
def main():
    members = [member_spec(TEAM[i], ASSIST[i]) for i in range(len(TEAM))]
    for ls in DB.card(TEAM[0].card_id).leader_skill.effects:
        print(ls)
    for m in members:
        ls_mult = 1
        main_dmg, sub_dmg = 0, 0
        for ls in itertools.chain(
                DB.card(TEAM[0].card_id).leader_skill.effects,
                DB.card(TEAM[1].card_id).leader_skill.effects):
            if not isinstance(ls, LS.BaseStatBoost):
                continue
            mult = ls.calculate_atk(COMBOS, TRIGGER, HP)
            if mult is not None and (
                    m.element in ls.elements or
                    m.sub_element in ls.elements or
                    any(t in ls.types for t in m.types)):
                ls_mult *= mult / 100

        awaken_mult = lambda a: a.damage_multiplier() ** m.awakenings.count(a)
        for c in COMBOS:
            if c.orb != m.element and c.orb != m.sub_element:
                continue
            dmg = math.ceil(m.atk * (1 + 0.25 * (c.size - 3)))

            if c.size == 4:
                dmg *= awaken_mult(TWO_WAY)
            elif c.shape == Shape.L:
                dmg *= awaken_mult(L_ATTACK)
            elif c.shape == Shape.SQUARE:
                dmg *= awaken_mult(VOID_DAMAGE_PIERCER)

            if c.orb == m.element:
                main_dmg += round(dmg)
            if c.orb == m.sub_element:
                if m.element == m.sub_element:
                    sub_dmg += math.ceil(dmg / 10)
                else:
                    sub_dmg += math.ceil(dmg / 3)


        combo_mult = (1 + 0.25 * (len(COMBOS) - 1))
        main_dmg = math.ceil(main_dmg * combo_mult)
        sub_dmg = math.ceil(sub_dmg * combo_mult)

        extra_mult = 1
        if len(COMBOS) >= 7:
            extra_mult *= awaken_mult(ENHANCED_COMBO)
        if len(COMBOS) >= 10:
            extra_mult *= awaken_mult(ENHANCED_10_COMBO)

        # TODO: check if this should happen in earlier phase
        if HP >= 80:
            extra_mult *= awaken_mult(EIGHTY_HP_ENHANCED)
        if HP <= 50:
            extra_mult *= awaken_mult(FIFTY_HP_ENHANCED)

        main_dmg = round(main_dmg * ls_mult * extra_mult)
        sub_dmg = round(sub_dmg * ls_mult * extra_mult)

        print(m.name, ' ' * (50 - wcwidth.wcswidth(m.name)),
              util.element_to_color(m.element), f'{main_dmg:>13,d}',
              util.element_to_color(m.sub_element), f'{sub_dmg:>13,d}',
              util.element_to_color(NO_ORB))

if __name__ == '__main__':
    main()
