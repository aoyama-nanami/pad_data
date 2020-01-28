import copy
import dataclasses
from typing import Any, Callable, List, Mapping, MutableMapping, Optional
import wcwidth

from pad_data import common

@dataclasses.dataclass
class Skill:
    name: str
    description: str
    effects: List[Any]
    turn_max: Optional[int]
    turn_min: Optional[int]

    @property
    def clean_description(self) -> str:
        return self.description.replace('\n', '')

@dataclasses.dataclass
class EnemySkillRef:
    enemy_skill_id: int
    enemy_ai: int
    enemy_rnd: int

def _unflatten(raw: List[Any], idx: int, width: int, replace: bool) -> None:
    """Unflatten a card array.

    Index is the slot containing the item count.
    Width is the number of slots per item.
    If replace is true, values are moved into an array at idx.
    If replace is false, values are deleted.
    """
    item_count = raw[idx]
    if item_count == 0:
        if replace:
            raw[idx] = list()
            return

    data_start = idx + 1
    flattened_item_count = width * item_count
    flattened_data_slice = slice(data_start, data_start + flattened_item_count)

    data = list(raw[flattened_data_slice])
    del raw[flattened_data_slice]

    if replace:
        raw[idx] = data

# pylint: disable=too-many-instance-attributes
class Card:
    def __init__(self, raw_data: List[str]):
        self._raw_data = raw_data
        self._parse_raw_data()
        self.skill = Skill('', '', [], 0, 0)
        self.leader_skill = Skill('', '', [], 0, 0)
        self.enemy_passive_resist: MutableMapping[int, Skill] = {}

    # Copied from
    # https://github.com/nachoapps/dadguide-data/blob/master/etl/pad/raw/card.py
    # and removed some fields for faster processing
    def _parse_raw_data(self) -> None:
        raw = self._raw_data

        _unflatten(raw, 57, 3, replace=True)
        _unflatten(raw, 58, 1, replace=True)

        self.card_id = int(raw[0])
        self.name = raw[1]
        self.attr_id = common.Orb(int(raw[2]))
        self.sub_attr_id = common.Orb(int(raw[3]))
        # 4: is_ult
        self.type = [common.Type(int(raw[5])),
                     common.Type(int(raw[6])),
                     common.Type.NO_TYPE]
        self.rarity = int(raw[7])
        self.cost = int(raw[8])

        # 9: Appears to be related to the size of the monster.
        # If 5, the monster always spawns alone. Needs more research.

        self.max_level = int(raw[10])
        self.feed_xp_per_level = int(raw[11]) // 4
        self.released_status = raw[12] == 100
        self.sell_gold_per_level = int(raw[13]) // 10

        self.min_hp = int(raw[14])
        self.max_hp = int(raw[15])
        self.hp_scale = float(raw[16])

        self.min_atk = int(raw[17])
        self.max_atk = int(raw[18])
        self.atk_scale = float(raw[19])

        self.min_rcv = int(raw[20])
        self.max_rcv = int(raw[21])
        self.rcv_scale = float(raw[22])

        self.xp_max = int(raw[23])
        self.xp_scale = float(raw[24])

        self.active_skill_id = int(raw[25])
        self.leader_skill_id = int(raw[26])

        # 27: Enemy turn timer for normal dungeons, and techs where
        # enemy_turns_alt is not populated.

        # 28~36: enemy hp/atk/def
        # Level range from 1 to 10

        # 37: enemy_max_level
        # 38: enemy_coins_per_level
        # 39: enemy_xp_per_level

        # 40: ancestor_id

        # 41~45: evo mat
        # 46~50: un-evo mat

        # enemy AI releated things
        # 51: enemy_turns_alt
        # When >0, the enemy turn timer for technical dungeons.
        # 52: use_new_ai
        # 53: enemy_skill_max_counter
        # 54: enemy_skill_counter_increment

        # 55~56: unknown

        es_data = list(map(int, raw[57]))
        self.enemy_skill_refs = [
            EnemySkillRef(*es_data[i : i + 3])
            for i in range(0, len(es_data) - 2, 3)]

        self.awakenings = [common.Awakening(x) for x in raw[58]]
        self.super_awakenings = [common.Awakening(int(x))
                                 for x in raw[59].split(',')
                                 if x.strip()]

        # 60: base_id
        # 61: group_id
        self.type[2] = common.Type(int(raw[62]))

        # 63: sell_mp
        # 64: latent_on_feed
        # 65: collab_id

        # Bitmap with some random flag values, not sure what they all do.
        self.random_flags = int(raw[66])

        self.inheritable = bool(self.random_flags & 1)
        self.is_collab = bool(self.random_flags & 4)

        self.furigana = str(raw[67])  # JP data only?
        self.limit_mult = int(raw[68])

        # 69: voice_id
        # 70: orb_skin_id

        self.other_fields = raw[71:]

    def _stat_at_level(self, st: str, lv: Optional[int]) -> int:
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
        'inheritable', 'leader_skill', 'limit_mult', 'max_atk', 'max_hp',
        'max_level', 'max_rcv', 'min_atk', 'min_hp', 'min_rcv', 'name',
        'rarity', 'skill', 'sub_attr_id', 'super_awakenings', 'type',
    ])

    @property
    def merged_json(self) -> Mapping[str, Any]:
        obj = copy.deepcopy(self.__dict__)
        obj['skill'] = {
            'name': self.skill.name,
            'description': self.skill.description,
            'turn_max': self.skill.turn_max,
            'turn_min': self.skill.turn_min,
            'effects': self.skill.effects,
        }
        obj['leader_skill'] = {
            'name': self.leader_skill.name,
            'description': self.leader_skill.description,
            'effects': self.leader_skill.effects,
        }
        obj['enemy_passive_resist'] = [
            {'name': s.name, 'effects': s.effects}
            for s in self.enemy_passive_resist.values()
        ]
        return dict((k, v) for k, v in obj.items()
                    if k in Card._FIELD_WHITELIST)

    def atk_at_level(self, level: Optional[int]=None) -> int:
        return self._stat_at_level('atk', level)

    def hp_at_level(self, level: Optional[int]=None) -> int:
        return self._stat_at_level('hp', level)

    def rcv_at_level(self, level: Optional[int]=None) -> int:
        return self._stat_at_level('rcv', level)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def dump(self, atk_eval: Callable[['Card'], int]=atk_at_level,
             rcv_eval: Callable[['Card'], int]=rcv_at_level,
             print_active_skill: bool=True, print_leader_skill: bool=False
             ) -> None:
        print(self.attr_id.color_code(),
              self.name,
              common.Orb.NO_ORB.color_code(),
              ' ' * (50 - wcwidth.wcswidth(self.name)),
              f'{self.hp_at_level():8}',
              f'{atk_eval(self):8}',
              f'{rcv_eval(self):8}',
              sep='',
              end='  ')

        if print_active_skill:
            print(f'{self.skill.turn_max:2}/{self.skill.turn_min:2} ',
                  self.skill.clean_description,
                  sep='',
                  end='')
        if print_leader_skill:
            print(self.leader_skill.clean_description, end='')
        print()
