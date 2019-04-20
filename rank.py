#! /usr/bin/env python3

import collections
import dataclasses
import typing
import wcwidth

from pad_data.database import Database
from pad_data.card import Card
from pad_data.common import Awakening, Orb, Type
from pad_data.util import import_enum_members, element_to_color

import_enum_members(Awakening, globals())
import_enum_members(Orb, globals())
import_enum_members(Type, globals())

def print_card(card, atk_eval=Card.atk_at_level, rcv_eval=Card.rcv_at_level):
    print(element_to_color(card.element),
          card.name,
          element_to_color(NO_ORB),
          ' ' * (50 - wcwidth.wcswidth(card.name)),
          f'{card.hp_at_level():6}',
          f'{atk_eval(card):8}',
          f'{rcv_eval(card):5}',
          sep='')

# pylint: disable=undefined-variable
@dataclasses.dataclass
class AtkEvaluator:
    LATENT_GOD_KILLER: typing.ClassVar[typing.Set[Type]] = \
        set((BALANCE, DEMON, MACHINE))
    LATENT_DRAGON_KILLER: typing.ClassVar[typing.Set[Type]] = \
        set((BALANCE, HEALER))
    LATENT_DEMON_KILLER: typing.ClassVar[typing.Set[Type]] = \
        set((BALANCE, GOD, ATTACK))
    LATENT_MACHINE_KILLER: typing.ClassVar[typing.Set[Type]] = \
        set((BALANCE, PHYSICAL, DRAGON))
    LATENT_BALANCE_KILLER: typing.ClassVar[typing.Set[Type]] = \
        set((BALANCE, MACHINE))
    LATENT_ATTACK_KILLER: typing.ClassVar[typing.Set[Type]] = \
        set((BALANCE, HEALER))
    LATENT_PHYSICAL_KILLER: typing.ClassVar[typing.Set[Type]] = \
        set((BALANCE, ATTACK))
    LATENT_HEALER_KILLER: typing.ClassVar[typing.Set[Type]] = \
        set((BALANCE, DRAGON, PHYSICAL))

    awakenings: typing.Set[Awakening] = dataclasses.field(default_factory=set)
    multi: bool = False
    elements: typing.Mapping[Orb, float] = \
        dataclasses.field(default_factory=dict)
    types: typing.Mapping[Type, float] = \
        dataclasses.field(default_factory=dict)

    target_enemy: dataclasses.InitVar[Card] = None
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
            e = target_enemy.element
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
                        latent_types |= \
                            getattr(AtkEvaluator, f'LATENT_{t.name}_KILLER')
                for t in latent_types:
                    self.types[t] *= 1.5 ** 3


    def __call__(self, card):
        atk = card.atk_at_level() + 495
        atk += card.awakenings.count(ENHANCED_ATK) * 100

        for a in self.awakenings:
            atk *= a.damage_multiplier() ** card.awakenings.count(a)

        if not self.multi:
            a = max(self.awakenings & set(card.super_awakenings),
                    default=Awakening.ENHANCED_HP, # somthing without damage
                    key=Awakening.damage_multiplier)
            atk *= a.damage_multiplier()

        atk *= self.elements[card.element]
        atk *= max(self.types[t] for t in card.type)

        return round(atk)

# pylint: disable=undefined-variable
def main():
    db = Database()
    cards = db.get_all_released_cards()

    config = AtkEvaluator(
        awakenings=[TWO_WAY, ENHANCED_COMBO, L_ATTACK],
        target_enemy=db.card(631),
        latent=True,
        )
    # cards = filter(lambda c: c.element in (FIRE, LIGHT), cards)
    cards = sorted(cards, key=config, reverse=True)
    cards = list(cards)
    for i in range(30):
        print_card(cards[i], atk_eval=config)

if __name__ == '__main__':
    main()
