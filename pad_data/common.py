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

    # TODO: rename after en version implemented these
    FIRE_COMBO_ENHANCED = 73
    WATER_COMBO_ENHANCED = 74
    WOOD_COMBO_ENHANCED = 75
    LIGHT_COMBO_ENHANCED = 76
    DARK_COMBO_ENHANCED = 77

    @property
    def damage_multiplier(self) -> float:
        # pylint: disable=no-member
        # pylint can't detect the type of enum name/value
        # https://github.com/PyCQA/pylint/issues/533
        if self.name.endswith('_KILLER'):
            return 3
        return _AWAKENING_DAMAGE_MAP.get(self, 1)

    @property
    def short_name(self) -> str:
        return _AWAKENING_SHORT_NAMES[self]

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

_AWAKENING_SHORT_NAMES = {
    Awakening.ENHANCED_HP : 'HP+',
    Awakening.ENHANCED_ATK : 'ATK+',
    Awakening.ENHANCED_RCV : 'RCV+',

    Awakening.REDUCE_FIRE_DMG : '火-',
    Awakening.REDUCE_WATER_DMG : '水-',
    Awakening.REDUCE_WOOD_DMG : '木-',
    Awakening.REDUCE_LIGHT_DMG : '光-',
    Awakening.REDUCE_DARK_DMG : '闇-',

    Awakening.AUTO_RECOVER : '自回',
    Awakening.RESIST_BIND : 'BIND',
    Awakening.RESIST_DARK : '暗闇',
    Awakening.RESIST_JAMMERS : '邪魔',
    Awakening.RESIST_POISON : '毒',

    Awakening.ENHANCED_FIRE_ORB : '火+',
    Awakening.ENHANCED_WATER_ORB : '水+',
    Awakening.ENHANCED_WOOD_ORB : '木+',
    Awakening.ENHANCED_LIGHT_ORB : '光+',
    Awakening.ENHANCED_DARK_ORB : '闇+',

    Awakening.EXTEND_TIME : '指',
    Awakening.RECOVER_BIND : '心列',
    Awakening.SKILL_BOOST : 'SB',

    Awakening.ENHANCED_FIRE_ATTR : '火列',
    Awakening.ENHANCED_WATER_ATTR : '水列',
    Awakening.ENHANCED_WOOD_ATTR : '木列',
    Awakening.ENHANCED_LIGHT_ATTR : '光列',
    Awakening.ENHANCED_DARK_ATTR : '闇列',

    Awakening.TWO_WAY : 'U',
    Awakening.RESIST_SKILL_BIND : 'Sx',
    Awakening.ENHANCED_HEART_ORB : '心+',
    Awakening.MULTI_BOOST : 'multi',

    Awakening.DRAGON_KILLER : '龍殺',
    Awakening.GOD_KILLER : '神殺',
    Awakening.DEMON_KILLER : '悪魔殺',
    Awakening.MACHINE_KILLER : '機殺',
    Awakening.BALANCE_KILLER : '平衡殺',
    Awakening.ATTACK_KILLER : '攻殺',
    Awakening.PHYSICAL_KILLER : '體殺',
    Awakening.HEALER_KILLER : '回殺',

    Awakening.EVOLVE_MATERIAL_KILLER : '進化殺',
    Awakening.AWAKEN_MATERIAL_KILLER : '覺醒殺',
    Awakening.ENHANCE_MATERIAL_KILLER : '強化殺',
    Awakening.VENDOR_MATERIAL_KILLER : '賣卻殺',

    Awakening.ENHANCED_COMBO : '7C',
    Awakening.GUARD_BREAK : '破防',
    Awakening.BONUS_ATTACK : '追打',
    Awakening.ENHANCED_TEAM_HP : 'TeamHP',
    Awakening.ENHANCED_TEAM_RCV : 'TeamRCV',
    Awakening.VOID_DAMAGE_PIERCER : '貫',
    Awakening.AWOKEN_ASSIST : 'E',
    Awakening.SUPER_BONUS_ATTACK : '超追打',
    Awakening.SKILL_CHARGE : '加速',
    Awakening.RESIST_BIND_PLUS : 'BIND+',
    Awakening.EXTEND_TIME_PLUS : '指+',
    Awakening.RESIST_CLOUD : '雲',
    Awakening.RESIST_IMMOBILITY : '封',

    Awakening.SKILL_BOOST_PLUS : 'SB+',
    Awakening.EIGHTY_HP_ENHANCED : '80',
    Awakening.FIFTY_HP_ENHANCED : '50',

    Awakening.L_SHIELD : 'L軽減',
    Awakening.L_ATTACK : 'L',
    Awakening.ENHANCED_10_COMBO : '10C',
    Awakening.COMBO_DROP : '枝豆',
    Awakening.SKILL_VOICE : '声',
    Awakening.DUNGEON_BONUS : '$',

    Awakening.REDUCE_HP : 'HP-',
    Awakening.REDUCE_ATK : 'ATK-',
    Awakening.REDUCE_RCV : 'RCV-',

    Awakening.RESIST_DARK_PLUS : '暗闇+',
    Awakening.RESIST_JAMMERS_PLUS : '邪魔+',
    Awakening.RESIST_POISON_PLUS : '毒+',

    Awakening.JAMMERS_ORBS_BLESSING : '邪魔加護',
    Awakening.POISON_ORBS_BLESSING : '毒加護',

    Awakening.FIRE_COMBO_ENHANCED: '火c',
    Awakening.WATER_COMBO_ENHANCED: '水c',
    Awakening.WOOD_COMBO_ENHANCED: '木c',
    Awakening.LIGHT_COMBO_ENHANCED: '光c',
    Awakening.DARK_COMBO_ENHANCED: '闇c',
}

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
            Orb.DARK: '1;35',
            Orb.JAMMER: '1:30',
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

