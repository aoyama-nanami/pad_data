from dataclasses import dataclass
from typing import List, Any

from .common import Awakening, Orb, Type

@dataclass
class Skill:
    name: str
    description: str
    effects: List[Any]
    turn_max: int
    turn_min: int

class Card:
    def __init__(self, json_data):
        self._json_data = json_data

    def __getattr__(self, name):
        return self._json_data[name]

    def __repr__(self):
        return self._json_data.__repr__()

    def _stat_at_level(self, st, lv):
        max_lv = self.max_level
        max_v = getattr(self, f'max_{st}')
        min_v = getattr(self, f'min_{st}')
        scale = getattr(self, f'{st}_scale')
        limit_mult = self.limit_mult

        if lv is None:
            lv = 110 if self.limit_mult > 0 else max_lv

        if max_lv == 1:
            # In this case, max_v may not equal to min_v.
            # e.g. http://pad.skyozora.com/pets/147
            # min_v is the correct number.
            return min_v

        if 1 <= lv <= max_lv:
            return round(
                min_v + (max_v - min_v) * ((lv - 1) / (max_lv - 1)) ** scale)

        # limit break should be in range [100, 110]
        if limit_mult > 0 and 100 <= lv <= 110:
            return round(max_v * (1 + limit_mult * (lv - 99) / 1100))

        raise ValueError('level out of range')

    def atk_at_level(self, level=None):
        return self._stat_at_level('atk', level)

    def hp_at_level(self, level=None):
        return self._stat_at_level('hp', level)

    def rcv_at_level(self, level=None):
        return self._stat_at_level('rcv', level)

    @property
    def awakenings(self):
        return list(map(Awakening, self._json_data['awakenings']))

    @property
    def super_awakenings(self):
        return list(map(Awakening, self._json_data['super_awakenings']))

    @property
    def element(self):
        return Orb(self.attr_id)

    @property
    def sub_element(self):
        return Orb(self.sub_attr_id)

    @property
    def type(self):
        return tuple(Type(getattr(self, f'type_{i}_id')) for i in range(1, 4))
