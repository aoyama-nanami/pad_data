#! /usr/bin/env python3

from dataclasses import dataclass
import decimal
import itertools
import math
from typing import List, Optional
import wcwidth

import path_common # pylint: disable=import-error,unused-import

from pad_data import database, util
from pad_data.common import Awakening, Combo, Latent, Orb, Shape, Type
from pad_data.leader_skill import effect as LS

util.import_enum_members(Awakening, globals())
util.import_enum_members(Orb, globals())
util.import_enum_members(Type, globals())
util.import_enum_members(Latent, globals())

decimal.getcontext().rounding = decimal.ROUND_HALF_UP

DB = database.Database()

@dataclass
class Team:
    card_id: int
    lv: int
    awakening_count: int = 9
    atk_plus: int = 99
    super_awakening: Optional[Awakening] = None
    latent: Optional[List[Latent]] = None

# BEGIN CONFIG

# pylint: disable=undefined-variable
TEAM = [
    Team(card_id=4016, lv=110, super_awakening=ENHANCED_COMBO,
         latent=[LATENT_MACHINE_KILLER] * 3),
    Team(card_id=5792, lv=110, super_awakening=L_ATTACK,
         latent=[LATENT_MACHINE_KILLER] * 3),
    Team(card_id=2568, lv=110),
    Team(card_id=5634, lv=101),
    Team(card_id=3945, lv=110),
    Team(card_id=5631, lv=99, latent=[LATENT_MACHINE_KILLER] * 3),
]
ASSIST = [
    None,
    Team(card_id=5813, lv=1, atk_plus=0),
    None,
    None,
    None,
    None,
]
# pylint: disable=undefined-variable
COMBOS = [
    Combo(FIRE, 5, Shape.L),
    Combo(WATER),
    Combo(WOOD),
    Combo(LIGHT),
    Combo(DARK),
    Combo(HEART),
]
TRIGGER = False
HP = 100
ENEMY_ID = 1091

# END CONFIG

@dataclass
class MemberSpec:
    name: str
    element: Orb
    sub_element: Optional[Orb]
    types: List[Type]
    atk: int
    awakenings: List[Awakening]
    latent: List[Latent]

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
        if card.attr_id == assist_card.attr_id:
            assist_atk = (assist_card.atk_at_level(assist.lv)
                          + assist_card.atk_plus * 5)
            atk += round(assist_atk * 0.05)

    atk += awakenings.count(ENHANCED_ATK) * 100
    atk -= awakenings.count(REDUCE_ATK) * 1000

    return MemberSpec(
        name=card.name,
        element=card.attr_id,
        sub_element=card.sub_attr_id,
        types=card.type,
        atk=atk,
        awakenings=awakenings,
        latent=base.latent if base.latent else [],
    )

def awaken_mult(card, awaken):
    return (decimal.Decimal(awaken.damage_multiplier) **
            card.awakenings.count(awaken))

def element_mult(self_element, target_element):
    assert self_element <= DARK
    assert target_element <= DARK
    assert target_element != NO_ORB

    if self_element == NO_ORB:
        return 0

    # fire/water/wood
    if self_element <= 2:
        if target_element == (self_element + 2) % 3:
            return 2
        if target_element == (self_element + 1) % 3:
            return decimal.Decimal(0.5)

    # light/dark
    if set([self_element, target_element]) == set([LIGHT, DARK]):
        return 2

    return 1

# pylint: disable=undefined-variable
def main():
    members = [member_spec(TEAM[i], ASSIST[i]) for i in range(len(TEAM))]
    enemy = DB.card(ENEMY_ID) if ENEMY_ID else None

    for ls in DB.card(TEAM[0].card_id).leader_skill.effects:
        print(ls)

    total_dmg = 0
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

        for c in COMBOS:
            if c.orb != m.element and c.orb != m.sub_element:
                continue
            # TODO: add enhanced orbs
            dmg = math.ceil(m.atk * (1 + 0.25 * (c.size - 3)))

            if c.size == 4:
                dmg = round(dmg * awaken_mult(m, TWO_WAY), 0)
            elif c.shape == Shape.L:
                dmg = round(dmg * awaken_mult(m, L_ATTACK), 0)
            elif c.shape == Shape.SQUARE:
                dmg = round(dmg * awaken_mult(m, VOID_DAMAGE_PIERCER), 0)

            if c.orb == m.element:
                main_dmg += dmg
            if c.orb == m.sub_element:
                if m.element == m.sub_element:
                    sub_dmg += math.ceil(dmg / 10)
                else:
                    sub_dmg += math.ceil(dmg / 3)

        combo_mult = decimal.Decimal(1 + 0.25 * (len(COMBOS) - 1))
        main_dmg = math.ceil(main_dmg * combo_mult)
        sub_dmg = math.ceil(sub_dmg * combo_mult)

        # TODO: check if this should happen in earlier phase
        extra_mult = 1
        if HP >= 80:
            extra_mult *= awaken_mult(m, EIGHTY_HP_ENHANCED)
        if HP <= 50:
            extra_mult *= awaken_mult(m, FIFTY_HP_ENHANCED)
        # TODO: add row attack multiplier

        main_dmg = round(main_dmg * extra_mult, 0)
        sub_dmg = round(sub_dmg * extra_mult, 0)

        combo_enh_mult = 1
        if len(COMBOS) >= 7:
            combo_enh_mult *= awaken_mult(m, ENHANCED_COMBO)
        if len(COMBOS) >= 10:
            combo_enh_mult *= awaken_mult(m, ENHANCED_10_COMBO)

        main_dmg = round(main_dmg * decimal.Decimal(combo_enh_mult), 0)
        sub_dmg = round(sub_dmg * decimal.Decimal(combo_enh_mult), 0)

        main_dmg = round(main_dmg * decimal.Decimal(ls_mult), 0)
        sub_dmg = round(sub_dmg * decimal.Decimal(ls_mult), 0)

        if enemy:
            main_dmg *= element_mult(m.element, enemy.attr_id)
            sub_dmg *= element_mult(m.sub_element, enemy.attr_id)

            for t in enemy.type:
                if t == NO_TYPE:
                    continue
                a = getattr(Awakening, f'{t.name}_KILLER', None)
                if a:
                    main_dmg *= awaken_mult(m, a)
                    sub_dmg *= awaken_mult(m, a)
                l = getattr(Latent, f'LATENT_{t.name}_KILLER', None)
                if l:
                    main_dmg *= decimal.Decimal(1.5) ** m.latent.count(l)
                    sub_dmg *= decimal.Decimal(1.5) ** m.latent.count(l)

        total_dmg += main_dmg + sub_dmg
        print(m.name, ' ' * (50 - wcwidth.wcswidth(m.name)),
              util.element_to_color(m.element), f'{int(main_dmg):>13,d}',
              util.element_to_color(m.sub_element), f'{int(sub_dmg):>13,d}',
              util.element_to_color(NO_ORB))
    print('')
    print(' ' * 60, f'Total: {int(total_dmg):>13,d}')

if __name__ == '__main__':
    main()
