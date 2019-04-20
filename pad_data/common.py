from dataclasses import dataclass
import enum
from typing import List, Any

@enum.unique
class Awakening(enum.Enum):
    ENHANCED_HP = 1
    ENHANCED_ATK = 2
    ENHANCED_RCV = 3

    REDUCE_FIRE_DMG = 4
    REDUCE_WATER_DMG = 5
    REDUCE_WOOD_DMG = 6
    REDUCE_LIGHT_DMG = 7
    REDUCE_DARK_DMG = 8

    AUTO_RECOVER = 9 # 自動回復
    RESIST_BIND = 10 # バインド耐性
    RESIST_DARK = 11
    RESIST_JAMMERS = 12
    RESIST_POISON = 13

    ENHANCED_FIRE_ORB = 14 # ドロップ強化
    ENHANCED_WATER_ORB = 15
    ENHANCED_WOOD_ORB = 16
    ENHANCED_LIGHT_ORB = 17
    ENHANCED_DARK_ORB = 18

    EXTEND_TIME = 19 # 操作時間延長
    RECOVER_BIND = 20 # バインド回復
    SKILL_BOOST = 21

    ENHANCED_FIRE_ATTR = 22 # 列強化
    ENHANCED_WATER_ATTR = 23
    ENHANCED_WOOD_ATTR = 24
    ENHANCED_LIGHT_ATTR = 25
    ENHANCED_DARK_ATTR = 26

    TWO_WAY = 27
    RESIST_SKILL_BIND = 28 # 封印耐性
    ENHANCED_HEART_ORB = 29 # 回復ドロップ強化
    MULTI_BOOST = 30

    GOD_KILLER = 31
    DRAGON_KILLER = 32
    DEMON_KILLER = 33
    MACHINE_KILLER = 34
    BALANCE_KILLER = 35
    ATTACK_KILLER = 36
    PHYSICAL_KILLER = 37
    HEALER_KILLER = 38

    EVOLVE_MATERIAL_KILLER = 39
    AWAKEN_MATERIAL_KILLER = 40
    ENHANCE_MATERIAL_KILLER = 41
    VENDOR_MATERIAL_KILLER = 42

    ENHANCED_COMBO = 43 # コンボ強化
    GUARD_BREAK = 44
    BONUS_ATTACK = 45 # 追加攻擊
    ENHANCED_TEAM_HP = 46
    ENHANCED_TEAM_RCV = 47
    VOID_DAMAGE_PIERCER = 48
    AWOKEN_ASSIST = 49 # 覚醒アシスト
    SUPER_BONUS_ATTACK = 50
    SKILL_CHARGE = 51
    RESIST_BIND_PLUS = 52
    EXTEND_TIME_PLUS = 53
    RESIST_CLOUD = 54
    RESIST_IMMOBILITY = 55 # 操作不可耐性

    SKILL_BOOST_PLUS = 56
    EIGHTY_HP_ENHANCED = 57
    FIFTY_HP_ENHANCED = 58

    L_SHIELD = 59
    L_ATTACK = 60
    ENHANCED_10_COMBO = 61
    COMBO_DROP = 62
    SKILL_VOICE = 63
    DUNGEON_BONUS = 64

    def damage_multiplier(self):
        if self.name.endswith('_KILLER'):
            return 3
        return _AWAKENING_DAMAGE_MAP.get(self, 1)

_AWAKENING_DAMAGE_MAP = {
    Awakening.TWO_WAY: 1.5,
    Awakening.MULTI_BOOST: 1.5,
    Awakening.L_ATTACK: 1.5,

    Awakening.ENHANCED_COMBO: 2,
    Awakening.SUPER_BONUS_ATTACK: 2,

    Awakening.VOID_DAMAGE_PIERCER: 2.5,

    Awakening.ENHANCED_10_COMBO: 5}

@enum.unique
class Orb(enum.Enum):
    NO_ORB = -1
    FIRE = 0
    WATER = 1
    WOOD = 2
    LIGHT = 3
    DARK = 4
    HEART = 5
    JAMMER = 6
    POISON = 7
    MORTAL_POISON = 8
    BOMB = 9

@enum.unique
class Type(enum.Enum):
    NO_TYPE = -1
    EVOLVE_MATERIAL = 0
    BALANCE = 1
    PHYSICAL = 2
    HEALER = 3
    DRAGON = 4
    GOD = 5
    ATTACK = 6
    DEMON = 7
    MACHINE = 8
    AWAKEN_MATERIAL = 12
    ENHANCE_MATERIAL = 14
    VENDOR_MATERIAL = 15

@dataclass
class Skill:
    name: str
    description: str
    effects: List[Any]


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
