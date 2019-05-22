import copy
import dataclasses
from typing import Any, List, Mapping
import wcwidth

from pad_data import common, util

@dataclasses.dataclass
class Skill:
    name: str
    clean_description: str
    description: str
    effects: List[Any]
    turn_max: int
    turn_min: int
    json_data: List[Mapping[str, Any]]

@dataclasses.dataclass
class EnemyPassiveResist:
    enemy_skill_id: int
    name: str
    skill_type: int  # 72: element resist, 118: type resist
    skill_name: str
    param: List[int]

class Card:
    def __init__(self, json_data):
        self._json_data = json_data
        self.skill = None
        self.leader_skill = None
        self.enemy_passive_resist = {}

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

    _FIELD_WHITELIST = set([
        'attr_id', 'awakenings', 'card_id', 'enemy_passive_resist',
        'inheritable', 'limit_mult', 'max_atk', 'max_hp', 'max_level',
        'max_rcv', 'min_atk', 'min_hp', 'min_rcv', 'name', 'skill',
        'sub_attr_id', 'super_awakenings', 'type',
    ])
    @property
    def merged_json(self):
        obj = copy.deepcopy(self._json_data)
        obj['type'] = [self.type_1_id, self.type_2_id, self.type_3_id]
        obj['skill'] = {
            'name': self.skill.name,
            'description': self.skill.description,
            'turn_max': self.skill.turn_max,
            'turn_min': self.skill.turn_min,
        }
        obj['skill']['effects'] = (
            list(map(lambda e: [type(e).__name__, e.__dict__],
                     self.skill.effects)))
        obj['enemy_passive_resist'] = (
            list(e.__dict__ for e in self.enemy_passive_resist.values()))
        return dict((k, v) for k, v in obj.items()
                    if k in Card._FIELD_WHITELIST)

    def atk_at_level(self, level=None):
        return self._stat_at_level('atk', level)

    def hp_at_level(self, level=None):
        return self._stat_at_level('hp', level)

    def rcv_at_level(self, level=None):
        return self._stat_at_level('rcv', level)

    @property
    def awakenings(self):
        return list(map(common.Awakening, self._json_data['awakenings']))

    @property
    def super_awakenings(self):
        return list(map(common.Awakening, self._json_data['super_awakenings']))

    @property
    def element(self):
        return common.Orb(self.attr_id)

    @property
    def sub_element(self):
        return common.Orb(self.sub_attr_id)

    @property
    def type(self):
        return tuple(common.Type(
            getattr(self, f'type_{i}_id')) for i in range(1, 4))

    def dump(self, atk_eval=atk_at_level, rcv_eval=rcv_at_level,
             print_skill=True):
        print(util.element_to_color(self.element),
              self.name,
              util.element_to_color(common.Orb.NO_ORB),
              ' ' * (50 - wcwidth.wcswidth(self.name)),
              f'{self.hp_at_level():8}',
              f'{atk_eval(self):8}',
              f'{rcv_eval(self):8}',
              sep='',
              end='  ')

        if print_skill:
            print(f'{self.skill.turn_max:2}/{self.skill.turn_min:2}',
                  self.skill.clean_description)
        else:
            print()
