#! /usr/bin/env python3

import collections
import dataclasses
from typing import Mapping, Set

import path_common # pylint: disable=import-error,unused-import

from pad_data import card, database
from pad_data.common import Awakening, Orb, Type
# pylint: disable=wildcard-import,unused-wildcard-import
from pad_data.util.global_enums import *

LATENT_KILLER = {
    'GOD': set((BALANCE, DEMON, MACHINE)),
    'DRAGON': set((BALANCE, HEALER)),
    'DEMON': set((BALANCE, GOD, ATTACK)),
    'MACHINE': set((BALANCE, PHYSICAL, DRAGON)),
    'BALANCE': set((BALANCE, MACHINE)),
    'ATTACK': set((BALANCE, HEALER)),
    'PHYSICAL': set((BALANCE, ATTACK)),
    'HEALER': set((BALANCE, DRAGON, PHYSICAL)),
}

@dataclasses.dataclass
class AtkEvaluator:
    awakenings: Set[Awakening] = dataclasses.field(default_factory=set)
    multi: bool = False
    elements: Mapping[Orb, float] = \
        dataclasses.field(default_factory=dict)
    types: Mapping[Type, float] = \
        dataclasses.field(default_factory=dict)

    target_enemy: dataclasses.InitVar[card.Card] = None
    latent: dataclasses.InitVar[bool] = False

    def __post_init__(self, target_enemy, latent):
        self.awakenings = set(self.awakenings)
        if self.multi:
            self.awakenings.add(MULTI_BOOST)
        self.elements = collections.defaultdict(
            lambda: 1, self.elements)
        self.types = collections.defaultdict(
            lambda: 1, self.types)

        if target_enemy is not None:
            e = target_enemy.attr_id
            if e == FIRE:
                self.elements[WATER] *= 2
                self.elements[WOOD] *= 0.5
            elif e == WATER:
                self.elements[WOOD] *= 2
                self.elements[FIRE] *= 0.5
            elif e == WOOD:
                self.elements[FIRE] *= 2
                self.elements[WATER] *= 0.5
            elif e == LIGHT:
                self.elements[DARK] *= 2
            elif e == DARK:
                self.elements[LIGHT] *= 2

            for t in target_enemy.type:
                if t == NO_TYPE:
                    continue
                killer = f'{t.name}_KILLER'
                self.awakenings.add(Awakening[killer])

            if latent:
                latent_types = set()
                for t in target_enemy.type:
                    if t == NO_TYPE:
                        continue
                    if t.name.endswith('_MATERIAL'):
                        latent_types |= set(Type)
                        latent_types.remove(NO_TYPE)
                    else:
                        latent_types |= LATENT_KILLER[t.name]
                for t in latent_types:
                    self.types[t] *= 1.5 ** 3


    def __call__(self, c):
        atk = c.atk_at_level() + 495
        atk += c.awakenings.count(ENHANCED_ATK) * 100

        for a in self.awakenings:
            atk *= a.damage_multiplier ** c.awakenings.count(a)

        if not self.multi:
            a = max(self.awakenings & set(c.super_awakenings),
                    default=Awakening.ENHANCED_HP, # somthing without damage
                    key=lambda a: a.damage_multiplier)
            atk *= a.damage_multiplier

        atk *= self.elements[c.attr_id]
        atk *= max(self.types[t] for t in c.type)

        return round(atk)

def main():
    db = database.Database()
    cards = db.get_all_released_cards()

    atk_eval = AtkEvaluator(
        awakenings=[TWO_WAY, ENHANCED_COMBO, L_ATTACK],
        target_enemy=db.card(631),
        latent=True,
        )
    # cards = filter(lambda c: c.attr_id in (FIRE, LIGHT), cards)
    cards = sorted(cards, key=atk_eval, reverse=True)
    cards = list(cards)
    for i in range(30):
        cards[i].dump(atk_eval=atk_eval)

if __name__ == '__main__':
    main()
