import dataclasses
import enum

@enum.unique
class Awakening(enum.IntEnum):
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

    DRAGON_KILLER = 31
    GOD_KILLER = 32
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

    REDUCE_HP = 65
    REDUCE_ATK = 66
    REDUCE_RCV = 67

    RESIST_DARK_PLUS = 68
    RESIST_JAMMERS_PLUS = 69
    RESIST_POISON_PLUS = 70

    JAMMERS_ORBS_BLESSING = 71
    POISON_ORBS_BLESSING = 72

    @property
    def damage_multiplier(self) -> float:
        # pylint: disable=no-member
        # pylint can't detect the type of enum name/value
        # https://github.com/PyCQA/pylint/issues/533
        if self.name.endswith('_KILLER'):
            return 3
        return _AWAKENING_DAMAGE_MAP.get(self, 1)

_AWAKENING_DAMAGE_MAP = {
    Awakening.TWO_WAY: 1.5,
    Awakening.MULTI_BOOST: 1.5,
    Awakening.L_ATTACK: 1.5,
    Awakening.EIGHTY_HP_ENHANCED: 1.5,

    Awakening.ENHANCED_COMBO: 2,
    Awakening.SUPER_BONUS_ATTACK: 2,
    Awakening.FIFTY_HP_ENHANCED: 2,
    Awakening.JAMMERS_ORBS_BLESSING: 2,
    Awakening.POISON_ORBS_BLESSING: 2,

    Awakening.VOID_DAMAGE_PIERCER: 2.5,

    Awakening.ENHANCED_10_COMBO: 5}

@enum.unique
class Orb(enum.IntEnum):
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

    def color_code(self) -> str:
        color_map = {
            Orb.NO_ORB: '',
            Orb.FIRE: '1;31',
            Orb.WATER: '1;36',
            Orb.WOOD: '1;32',
            Orb.LIGHT: '1;33',
            Orb.DARK: '1;35'
        }

        return f'\x1b[{color_map[self]}m'

@enum.unique
class Type(enum.IntEnum):
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

@enum.unique
class EnemySkill(enum.IntEnum):
    # TODO: implement full list
    VOID_SHIELD = 71
    SKILL_SET = 83  # set of multiple skills id in args

    # passive skill
    ELEMENT_RESIST = 72
    TYPE_RESIST = 118

@enum.unique
class Shape(enum.IntEnum):
    OTHER = 0
    L = 1
    CROSS = 2
    ROW = 3
    SQUARE = 4

@dataclasses.dataclass
class Combo:
    orb: Orb
    size: int = 3
    shape: Shape = Shape.OTHER

# TODO: rename this
CCombo = Combo

@enum.unique
class Latent(enum.Enum):
    LATENT_GOD_KILLER = enum.auto()
    LATENT_DRAGON_KILLER = enum.auto()
    LATENT_DEMON_KILLER = enum.auto()
    LATENT_MACHINE_KILLER = enum.auto()
    LATENT_BALANCE_KILLER = enum.auto()
    LATENT_ATTACK_KILLER = enum.auto()
    LATENT_PHYSICAL_KILLER = enum.auto()
    LATENT_HEALER_KILLER = enum.auto()

@enum.unique
class EvoType(enum.Enum):
    NO_EVO = 0
    NORMAL_EVO = 1
    ULTIMATE = 2
    REINCARNATION = 3
    SUPER_REINCARNATION = 4
    PIXEL = 5
    ASSIST = 6

