#! /usr/bin/env python3

from dataclasses import dataclass
import decimal
import itertools
import math
from typing import List, Optional, Union
import wcwidth

import path_common # pylint: disable=import-error,unused-import

from pad_data import database
from pad_data.common import Awakening, Combo, Latent, Orb, Shape, Type
from pad_data.leader_skill import effect as LS
# pylint: disable=wildcard-import,unused-wildcard-import
from pad_data.util.global_enums import *

decimal.getcontext().rounding = decimal.ROUND_HALF_UP
FixedPoint = Union[int, decimal.Decimal]

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

TEAM = [
    # L & F
    Team(card_id=6399, lv=99),
    Team(card_id=6399, lv=99),
    # teams
    Team(card_id=6409, lv=110, super_awakening=ENHANCED_COMBO,
         latent=[LATENT_MACHINE_KILLER] * 3),
    Team(card_id=6406, lv=108, latent=[LATENT_MACHINE_KILLER] * 1),
    Team(card_id=6109, lv=110, super_awakening=L_ATTACK,
         latent=[LATENT_DEMON_KILLER] * 3),
    Team(card_id=5940, lv=109, latent=[LATENT_MACHINE_KILLER] * 3),
]
ASSIST = [
    Team(card_id=6239, lv=1, atk_plus=0),
    None,
    None,
    None,
    None,
    None,
]
COMBOS = [
    Combo(FIRE),
    Combo(WATER),
    Combo(WOOD, size=3),
    Combo(WOOD, size=3),
    Combo(LIGHT, size=4),
    Combo(DARK),

    Combo(HEART),
    Combo(HEART),
    Combo(HEART),
    Combo(HEART),
    Combo(HEART),
    Combo(HEART),
]
TRIGGER = False
HP = 100
ENEMY_ID = 6081
DAMAGE_BUFF_MULT = 7.3

# END CONFIG

@dataclass
class MemberSpec:
    name: str
    element: Orb
    sub_element: Orb
    types: List[Type]
    atk: int
    awakenings: List[Awakening]
    latent: List[Latent]

def member_spec(base: Team, assist: Optional[Team]) -> MemberSpec:
    card = DB.card(base.card_id)
    atk = card.atk_at_level(base.lv) + base.atk_plus * 5
    assert base.awakening_count == 9
    awakenings = card.awakenings[:]
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
                          + assist.atk_plus * 5)
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

def awaken_mult(card: MemberSpec, awaken: Awakening) -> decimal.Decimal:
    return (decimal.Decimal(awaken.damage_multiplier) **
            card.awakenings.count(awaken))

def element_mult(self_element: Orb, target_element: Orb) -> FixedPoint:
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

def main() -> None:
    members = [member_spec(TEAM[i], ASSIST[i]) for i in range(len(TEAM))]
    enemy = DB.card(ENEMY_ID) if ENEMY_ID else None

    for ls in DB.card(TEAM[0].card_id).leader_skill.effects:
        print(ls)

    total_dmg = 0
    for m in members:
        ls_mult: FixedPoint = 1
        main_dmg: FixedPoint = 0
        sub_dmg: FixedPoint = 0

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
                ls_mult *= decimal.Decimal(mult) / 100

        for c in COMBOS:
            if c.orb != m.element and c.orb != m.sub_element:
                continue
            # TODO: add enhanced orbs
            dmg = math.ceil(m.atk * (1 + 0.25 * (c.size - 3)))

            if c.size == 4:
                dmg = round(dmg * awaken_mult(m, TWO_WAY))
            elif c.shape == Shape.L:
                dmg = round(dmg * awaken_mult(m, L_ATTACK))
            elif c.shape == Shape.SQUARE:
                dmg = round(dmg * awaken_mult(m, VOID_DAMAGE_PIERCER))

            if c.orb == m.element:
                main_dmg += dmg
            if c.orb == m.sub_element:
                if m.element == m.sub_element:
                    sub_dmg += math.ceil(dmg / 10)
                elif m.element == Orb.JAMMER:
                    sub_dmg += dmg
                else:
                    sub_dmg += math.ceil(dmg / 3)

        combo_mult = decimal.Decimal(1 + 0.25 * (len(COMBOS) - 1))
        main_dmg = math.ceil(main_dmg * combo_mult)
        sub_dmg = math.ceil(sub_dmg * combo_mult)

        # TODO: check if this should happen in earlier phase
        extra_mult: FixedPoint = 1
        if HP >= 80:
            extra_mult *= awaken_mult(m, EIGHTY_HP_ENHANCED)
        elif HP <= 50:
            extra_mult *= awaken_mult(m, FIFTY_HP_ENHANCED)
        # TODO: add row attack multiplier

        main_dmg = round(main_dmg * extra_mult)
        sub_dmg = round(sub_dmg * extra_mult)

        combo_enh_mult: FixedPoint = 1
        if len(COMBOS) >= 7:
            combo_enh_mult *= awaken_mult(m, ENHANCED_COMBO)
        if len(COMBOS) >= 10:
            combo_enh_mult *= awaken_mult(m, ENHANCED_10_COMBO)

        main_dmg = round(main_dmg * decimal.Decimal(combo_enh_mult))
        sub_dmg = round(sub_dmg * decimal.Decimal(combo_enh_mult))

        main_dmg = round(main_dmg * decimal.Decimal(ls_mult))
        sub_dmg = round(sub_dmg * decimal.Decimal(ls_mult))

        main_dmg *= decimal.Decimal(DAMAGE_BUFF_MULT)
        sub_dmg *= decimal.Decimal(DAMAGE_BUFF_MULT)

        if enemy:
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

            # min() before calculate element multiplier so damage will cap
            # at 1B
            main_dmg = min(main_dmg, 2 ** 31 - 1)
            sub_dmg = min(sub_dmg, 2 ** 31 - 1)

            main_dmg *= element_mult(m.element, enemy.attr_id)
            sub_dmg *= element_mult(m.sub_element, enemy.attr_id)

        main_dmg = min(main_dmg, 2 ** 31 - 1)
        sub_dmg = min(sub_dmg, 2 ** 31 - 1)

        total_dmg += int(main_dmg + sub_dmg)
        print(m.name, ' ' * (50 - wcwidth.wcswidth(m.name)),
              m.element.color_code(), f'{int(main_dmg):>13,d}',
              m.sub_element.color_code(), f'{int(sub_dmg):>13,d}',
              NO_ORB.color_code())
    print('')
    if enemy:
        print(enemy.attr_id.color_code(), enemy.name, NO_ORB.color_code(),
              ' ' * (60 - wcwidth.wcswidth(enemy.name)),
              f'Total: {int(total_dmg):>14,d}',
              sep='')

    else:
        print(' ' * 60, f'Total: {int(total_dmg):>13,d}')

if __name__ == '__main__':
    main()
