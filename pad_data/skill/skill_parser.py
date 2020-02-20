import functools
import itertools
from typing import Any, Callable, Generic, Iterator, List, TypeVar

from pad_data.active_skill import effect as AS
from pad_data.common import Orb, Type
from pad_data.enemy_skill import effect as ES
from pad_data.leader_skill import effect as LS
from pad_data.skill import SkillEffectTag

# special skill type for combined skill effect
ACTIVE_SKILL_SET = 116
LEADER_SKILL_SET = 138

T = TypeVar('T')

def _consume_all_args(func: Callable[[int], T], end: int
                      ) -> Callable[[Iterator[int]], List[T]]:
    def inner(func: Callable[[int], T], end: int, it: Iterator[int]
              ) -> List[Any]:
        return [func(x) for x in itertools.takewhile(lambda x: x > end, it)]
    return functools.partial(inner, func, end)

def orb_list(bit_mask: int) -> List[Orb]:
    return [Orb(i) for i in range(32) if (1 << i) & bit_mask]

def type_list(bit_mask: int) -> List[Type]:
    return [Type(i) for i in range(32) if (1 << i) & bit_mask]

class Ref:
    def __init__(self, name: str):
        self.name = name

class Unused(Generic[T]):
    def __init__(self, *values: T):
        self.values = values

    def __contains__(self, x: T) -> bool:
        return x in self.values

class Map:
    # TODO: type this 'Any'
    def __init__(self, cls: Callable[..., SkillEffectTag], **kwargs: Any):
        self._cls = cls
        self._kwargs = kwargs

    def __call__(self, *args: int) -> SkillEffectTag:
        args_iter = iter(args)
        g = itertools.chain(args_iter, itertools.repeat(0, 16))

        def convert(x: Any) -> Any:
            if isinstance(x, list):
                return list(map(convert, x))
            if isinstance(x, tuple):
                return tuple(map(convert, x))
            if isinstance(x, functools.partial):
                return x(g)
            if isinstance(x, Ref):
                return x
            if isinstance(x, Unused):
                assert next(g) in x
                return x
            if callable(x):
                return x(next(g))
            return x

        kwargs = {k: convert(v) for k, v in self._kwargs.items()}
        kwargs = {k: (kwargs[v.name] if isinstance(v, Ref) else v)
                  for k, v in kwargs.items()
                  if not isinstance(v, Unused)}

        obj = self._cls(**kwargs)

        try:
            if self._cls.__module__ != 'pad_data.enemy_skill.effect':
                next(args_iter)
                assert False, 'args not fully consumed!'
        except StopIteration:
            pass

        return obj

_AS_EFFECT_MAP = {
    0: Map(AS.AtkNuke, element=Orb, percentage=int, target=AS.Target.ALL),
    1: Map(AS.AtkNuke, element=Orb, value=int, target=AS.Target.ALL),
    2: Map(AS.AtkNuke, element=Orb.NO_ORB, percentage=int,
           target=AS.Target.ONE, percentage_upper=int),
    3: Map(AS.DamageReduction, duration=int, percentage=int),
    4: Map(AS.Poison, percentage=int),
    5: Map(AS.ChangeTheWorld, second=int),
    6: Map(AS.Gravity, percentage=int),
    7: Map(AS.Heal, rcv_percentage=int, bind=0, hp_value=0, hp_percentage=0,
           awoken_bind=0),
    8: Map(AS.Heal, hp_value=int, bind=0, rcv_percentage=0, hp_percentage=0,
           awoken_bind=0),
    9: Map(AS.OrbChange, from_=[Orb], to=[Orb]),
    10: Map(AS.OrbRefresh),
    18: Map(AS.DelayEnemyAttack, duration=int, unused=int),
    19: Map(AS.DefenseReduction, duration=int, percentage=int),
    20: Map(AS.DoubleOrbChange, from1=Orb, to1=Orb, from2=Orb, to2=Orb),
    21: Map(AS.ElementDamageReduction, duration=int, element=Orb,
            percentage=int),
    35: Map(AS.AtkNuke, element=Orb.NO_ORB, percentage=int, leech=int,
            target=AS.Target.ONE),
    37: Map(AS.AtkNuke, element=Orb, percentage=int, target=AS.Target.ONE),
    42: Map(AS.AtkNuke, target=Orb, element=Orb, value=int),
    50: Map(AS.ElementDamageBuff, duration=int, cond=[Orb], percentage=int),
    51: Map(AS.Cleave, duration=int),
    52: Map(AS.OrbEnhance, orbs=[Orb], unused=Unused(6, 100)),
    55: Map(AS.AtkNuke, target=AS.Target.ONE, element=Orb.NO_ORB,
            ignore_def=True, value=int),
    56: Map(AS.AtkNuke, target=AS.Target.ALL, element=Orb.NO_ORB,
            ignore_def=True, value=int),
    58: Map(AS.AtkNuke, target=AS.Target.ALL, element=Orb, percentage=int,
            percentage_upper=int),
    59: Map(AS.AtkNuke, target=AS.Target.ONE, element=Orb, percentage=int,
            percentage_upper=int),
    60: Map(AS.Counter, duration=int, percentage=int, element=Orb),
    71: Map(AS.AllOrbChange, orbs=_consume_all_args(Orb, -1)),
    84: Map(AS.AtkNuke, target=AS.Target.ONE, element=Orb, percentage=int,
            percentage_upper=int, hp_remain=int),
    85: Map(AS.AtkNuke, target=AS.Target.ALL, element=Orb, percentage=int,
            percentage_upper=int, hp_remain=int),
    86: Map(AS.AtkNuke, element=Orb, value=int, unused=Unused(0),
            hp_remain=int, target=AS.Target.ONE),
    87: Map(AS.AtkNuke, element=Orb, value=int, unused=Unused(0),
            hp_remain=int, target=AS.Target.ALL),
    88: Map(AS.TypeDamageBuff, duration=int, cond=[Type], percentage=int),
    90: Map(AS.ElementDamageBuff, duration=int, cond=[Orb, Orb],
            percentage=int),
    91: Map(AS.OrbEnhance, orbs=[Orb, Orb], unused=Unused(6)),
    92: Map(AS.TypeDamageBuff, duration=int, cond=[Type, Type], percentage=int),
    93: Map(AS.LeaderSwap),
    110: Map(AS.RemainingHpNuke, target=AS.Target, element=Orb, percentage=int,
             percentage_upper=int, unused=Unused(300)),
    115: Map(AS.AtkNuke, target=AS.Target.ONE, element=Orb, percentage=int,
             leech=int),
    116: Map(AS.SkillSet, skill_ids=_consume_all_args(int, 0)),
    117: Map(AS.Heal, bind=int, rcv_percentage=int, hp_value=int,
             hp_percentage=int, awoken_bind=int),
    118: Map(AS.RandomSkill, unused_skill_id=_consume_all_args(int, 0)),
    126: Map(AS.Skyfall, orbs=orb_list, duration=int, unused=int,
             percentage=int),
    127: Map(AS.ColumnChange, pos1=int, orb1=orb_list, pos2=int, orb2=orb_list),
    128: Map(AS.RowChange, pos1=int, orb1=orb_list, pos2=int, orb2=orb_list),
    132: Map(AS.MoveTimeExtend, duration=int, decisecond=int, percentage=int),
    140: Map(AS.OrbEnhance, orbs=orb_list, unused=Unused(6)),
    141: Map(AS.RandomOrbSpawn, count=int, orb=orb_list, exclude=orb_list),
    142: Map(AS.SelfElementChange, duration=int, element=Orb),
    143: Map(AS.TeamHpNuke, percentage=int, element=Orb,
             target=AS.Target.ALL),
    144: Map(AS.TeamElementAtkNuke, base_elem=orb_list, percentage=int,
             target=AS.Target, element=Orb),
    145: Map(AS.TeamRcvBasedHeal, percentage=int),
    146: Map(AS.ReduceCooldown, turn=[int, int]),
    152: Map(AS.Lock, orbs=orb_list, unused=Unused(42, 99)),
    153: Map(AS.EnemyElementChange, element=Orb, unused=Unused(1)),
    154: Map(AS.OrbChange, from_=orb_list, to=orb_list),
    156: Map(AS.awakening_based_skill, duration=int, awakenings=[int, int, int],
             mode=int, percentage=int),
    160: Map(AS.ComboIncrease, duration=int, combo=int),
    161: Map(AS.TrueGravity, percentage=int),
    # TODO: Need verify
    168: Map(AS.DamageBuffByAwakening, duration=int, awakenings=[int, int, int],
             unused1=Unused(0), unused2=Unused(0), unused3=Unused(0),
             percentage=int),
    172: Map(AS.Unlock),
    173: Map(AS.IgnoreAbsorb, duration=int, element=bool,
             unused=Unused(0), damage=bool),
    176: Map(AS.BoardChange, rows=[int, int, int, int, int], orb=Orb),
    179: Map(AS.HealOverTime, duration=int, unused=Unused(0), hp_percentage=int,
             bind=int, awoken_bind=int, rcv_percentage=0, hp_value=0),
    180: Map(AS.SkyfallEnhancedOrbs, duration=int, percentage=int),
    184: Map(AS.NoSkyfall, duration=int),
    # 敵1体に N の固定ダメージ x M 回, represented by array of M following item.
    188: Map(AS.AtkNuke, target=AS.Target.ONE, element=Orb.NO_ORB,
             ignore_def=True, value=int),
    189: Map(AS.ComboHelper),
    191: Map(AS.VoidDamagePiercer, duration=int),
    195: Map(AS.Sacrifice, hp_remain=int),
    196: Map(AS.UnmatchableRecover, turn=int),
    # 変身
    202: Map(AS.Transform, to=int),
    205: Map(AS.SkyfallLockedOrbs, orbs=orb_list, duration=int),
}

_LS_EFFECT_MAP = {
    11: Map(LS.StatBoost, elements=[Orb], types=[], atk=int),
    # ドロップを消した時、攻撃力n倍の追い打ち
    12: Map(LS.ExtraAttack, atk=int),
    # ドロップを消した時、回復力n倍のHPを回復
    13: Map(LS.ExtraHeal, rcv=int),
    # 根性, unused = proc rate?
    14: Map(LS.Resolve, hp_threshold=int, unused=Unused(100)),
    15: Map(LS.ExtendedBoost, move_time_extend=int),
    16: Map(LS.StatBoost, dr_elements=LS.BaseStatBoost.ALL_ELEM, dr=int),
    17: Map(LS.StatBoost, dr_elements=[Orb], dr=int),
    22: Map(LS.StatBoost, elements=[], types=[Type], atk=int),
    23: Map(LS.StatBoost, elements=[], types=[Type], hp=int),
    24: Map(LS.StatBoost, elements=[], types=[Type], rcv=int),
    26: Map(LS.StatBoost, atk=int),
    28: Map(LS.StatBoost, elements=[Orb], types=[], atk=int, rcv=Ref('atk')),
    29: Map(LS.StatBoost, elements=[Orb], types=[], hp=int, atk=Ref('hp'),
            rcv=Ref('hp')),
    30: Map(LS.StatBoost, elements=[], types=[Type, Type], hp=int),
    31: Map(LS.StatBoost, elements=[], types=[Type, Type], atk=int),
    # ドロップ操作時に太鼓の音が鳴る
    33: Map(LS.TaikoNoise),
    36: Map(LS.StatBoost, dr_elements=[Orb, Orb], dr=int),
    # TODO:
    # 3390-神国の魔術神・オーディン has a strange value:
    #   [100, 100, 80]
    38: Map(LS.HpBelow, hp_below=int, proc_rate=int, dr=int),
    39: Map(LS.by_stat_id(LS.HpBelow), hp_below=int, stat_id_list=[int, int],
            percentage=int),
    40: Map(LS.StatBoost, elements=[Orb, Orb], types=[], atk=int),
    41: Map(LS.CounterLS, proc_rate=int, atk=int, orb=Orb),
    43: Map(LS.HpAbove, hp_above=int, proc_rate=int, dr=int),
    44: Map(LS.by_stat_id(LS.HpAbove), hp_above=int, stat_id_list=[int, int],
            percentage=int),
    45: Map(LS.StatBoost, elements=[Orb], types=[], hp=int, atk=Ref('hp')),
    46: Map(LS.StatBoost, elements=[Orb, Orb], types=[], hp=int),
    48: Map(LS.StatBoost, elements=[Orb], types=[], hp=int),
    49: Map(LS.StatBoost, elements=[Orb], types=[], rcv=int),

    53: Map(LS.TreasureLootUp, percentage=int),
    54: Map(LS.GoldLootUp, percentage=int),

    # n色以上同時攻擊で攻撃力がx倍、最大m色y倍
    61: Map(LS.Rainbow, orbs=orb_list, color_min=int, atk=int, atk_step=int,
            color_step=int),
    62: Map(LS.StatBoost, elements=[], types=[Type], hp=int, atk=Ref('hp')),
    63: Map(LS.StatBoost, elements=[], types=[Type], hp=int, rcv=Ref('hp')),
    64: Map(LS.StatBoost, elements=[], types=[Type], atk=int, rcv=Ref('atk')),
    65: Map(LS.StatBoost, elements=[], types=[Type], hp=int, atk=Ref('hp'),
            rcv=Ref('hp')),
    66: Map(LS.Combo, combo=int, atk=int),
    67: Map(LS.StatBoost, elements=[Orb], types=[], hp=int, rcv=Ref('hp')),
    69: Map(LS.StatBoost, elements=[Orb], types=[Type], atk=int),
    73: Map(LS.StatBoost, elements=[Orb], types=[Type], hp=int, atk=Ref('hp')),
    75: Map(LS.StatBoost, elements=[Orb], types=[Type], atk=int,
            rcv=Ref('atk')),
    76: Map(LS.StatBoost, elements=[Orb], types=[Type], hp=int, atk=Ref('hp'),
            rcv=Ref('hp')),
    77: Map(LS.StatBoost, elements=[], types=[Type, Type], hp=int,
            atk=Ref('hp')),
    79: Map(LS.StatBoost, elements=[], types=[Type, Type], atk=int,
            rcv=Ref('atk')),

    94: Map(LS.by_stat_id(LS.HpBelow), hp_below=int, elements=[Orb],
            stat_id_list=[int, int], percentage=int),
    95: Map(LS.by_stat_id(LS.HpBelow), hp_below=int, types=[Type],
            stat_id_list=[int, int], percentage=int),
    96: Map(LS.by_stat_id(LS.HpAbove), hp_above=int, elements=[Orb],
            stat_id_list=[int, int], percentage=int),
    97: Map(LS.by_stat_id(LS.HpAbove), hp_above=int, types=[Type],
            stat_id_list=[int, int], percentage=int),

    98: Map(LS.Combo, combo=int, atk=int, atk_step=int, combo_max=int),

    100: Map(LS.by_stat_id(LS.Trigger), stat_id_list=[int, int],
             percentage=int),
    # 【落ちコンなし】nコンボちょうど
    101: Map(LS.ComboExact, combo=int, atk=int),
    103: Map(LS.by_stat_id(LS.Combo), combo=int, stat_id_list=[int, int],
             percentage=int),
    104: Map(LS.by_stat_id(LS.Combo), combo=int, elements=orb_list,
             stat_id_list=[int, int], percentage=int),
    # 総回復力が半減する、攻撃力がn倍
    105: Map(LS.StatBoost, rcv=int, atk=int),
    # 総HPが半減する、攻撃力がn倍
    106: Map(LS.StatBoost, hp=int, atk=int),
    # 総HPが減少するが
    107: Map(LS.StatBoost, hp=int),
    # 総HPが半減するが、xタイプの攻撃力がn倍。
    108: Map(LS.StatBoost, hp=int, elements=[], types=[Type], atk=int),
    109: Map(LS.ConnectedOrbs, orbs=orb_list, size=int, atk=int),
    111: Map(LS.StatBoost, elements=[Orb, Orb], types=[], hp=int,
             atk=Ref('hp')),
    114: Map(LS.StatBoost, elements=[Orb, Orb], types=[], hp=int,
             atk=Ref('hp'), rcv=Ref('hp')),
    119: Map(LS.ConnectedOrbs, orbs=orb_list, size=int, atk=int, atk_step=int,
             size_max=int),
    121: Map(LS.StatBoost, elements=orb_list, types=type_list, hp=int, atk=int,
             rcv=int),
    122: Map(LS.HpBelow, hp_below=int, elements=orb_list, types=type_list,
             atk=int, rcv=int),
    123: Map(LS.HpAbove, hp_above=int, elements=orb_list, types=type_list,
             atk=int, rcv=int),

    # Damage based on number of combos matched the given list
    # e.g.
    # [4, 4, 4, 4, 0, 2, 600, 200] -> 木2c 6倍, 最大4c 10倍
    # [8, 8, 1, 1, 0, 3, 350, 250] -> 光光火（光火火）の3コンボで攻撃力が3.5倍、
    #                                 光光火火の4コンボ以上で攻撃力が6倍
    124: Map(LS.ElementCombo, combo_list=[orb_list] * 5, combo_min=int, atk=int,
             atk_step=int),
    # e.g. 進化後ギニュー特戦隊がチームにそろっていると
    125: Map(LS.TeamStatBoost, card_ids=[int] * 5, hp=int, atk=int, rcv=int),

    129: Map(LS.StatBoost, elements=orb_list, types=type_list, hp=int, atk=int,
             rcv=int, dr_elements=orb_list, dr=int),
    130: Map(LS.HpBelow, hp_below=int, elements=orb_list, types=type_list,
             atk=int, rcv=int, dr_elements=orb_list, dr=int),
    131: Map(LS.HpAbove, hp_above=int, elements=orb_list, types=type_list,
             atk=int, rcv=int, dr_elements=orb_list, dr=int),
    # スキル使用時
    133: Map(LS.Trigger, elements=orb_list, types=type_list, atk=int, rcv=int),
    136: Map(LS.double_stat_boost,
             params_0=(orb_list, [], int, int, int),
             params_1=(orb_list, [], int, int, int)),
    137: Map(LS.double_stat_boost,
             params_0=([], type_list, int, int, int),
             params_1=([], type_list, int, int, int)),
    138: Map(LS.SkillSetLS, skill_ids=_consume_all_args(int, 0)),
    # e.g.
    #   HP満タンか50％以下で木属性の攻撃力が4倍。
    #   = [4, 0, 100, 0, 400, 50, 1, 400]
    # spec = (hp, 0/1=above/below, atk)
    139: Map(LS.hp_cond_139, elements=orb_list, types=type_list,
             spec=[[int, int, int]] * 2),
    148: Map(LS.RankExpUp, percentage=int),
    # 回復の4個消し
    149: Map(LS.ConnectedOrbs, orbs=[Orb.HEART], size=4, rcv=int),
    150: Map(LS.EnhancedOrbs5, unused=Unused(0), atk=int),
    151: Map(LS.HeartCross, atk=int, unused=Unused(0), dr=int),
    155: Map(LS.MultiplayerGame, elements=orb_list, types=type_list, hp=int,
             atk=int, rcv=int),
    # 5個十字消し1個につき攻撃力がn倍
    # arg is a list of 2-tuple: (orb, atk)
    157: Map(LS.CrossAtkBoost, args=[[Orb, int]] * 5),
    # ドロップをn個以下で消せない
    158: Map(LS.MatchFourOrAbove, match=int, elements=orb_list, types=type_list,
             atk=int, hp=int, rcv=int),
    159: Map(LS.ConnectedOrbs, orbs=orb_list, size=int, atk=int, atk_step=int,
             size_max=int),

    162: Map(LS.Board7x6),
    163: Map(LS.NoSkyfallLS, elements=orb_list, types=type_list, hp=int,
             atk=int, rcv=int, dr_elements=orb_list, dr=int),
    # see id 124
    164: Map(LS.ElementCombo, combo_list=[orb_list] * 4, combo_min=int, atk=int,
             rcv=int, atk_step=int, rcv_step=Ref('atk_step')),
    # n色以上同時攻撃で攻撃力と回復力が上昇、最大m倍
    165: Map(LS.Rainbow, orbs=orb_list, color_min=int, atk=int, rcv=int,
             atk_step=int, rcv_step=int, color_step=int),
    166: Map(LS.Combo, combo=int, atk=int, rcv=int, atk_step=int, rcv_step=int,
             combo_max=int),
    167: Map(LS.ConnectedOrbs, orbs=orb_list, size=int, atk=int, rcv=int,
             atk_step=int, rcv_step=int, size_max=int),
    169: Map(LS.Combo, combo=int, atk=int, dr=int),
    170: Map(LS.Rainbow, orbs=orb_list, color_min=int, atk=int, dr=int),
    # see id 124
    171: Map(LS.ElementCombo, combo_list=[orb_list] * 4, combo_min=int, atk=int,
             dr=int),
    175: Map(LS.CollaboTeamStatBoost, collabo_ids=[int] * 3, hp=int, atk=int,
             rcv=int),
    177: Map(LS.OrbRemaining, elements=orb_list, types=type_list, hp=int,
             atk_non_step=int, rcv=int, threshold=int, atk=int, atk_step=int),
    178: Map(LS.FixedMovementTime, seconds=int, elements=orb_list,
             types=type_list, hp=int, atk=int, rcv=int),

    # xをn個以上つなげて消す
    182: Map(LS.ConnectedOrbs, orbs=orb_list, size=int, atk=int, dr=int),

    183: Map(LS.hp_cond_183, elements=orb_list, types=type_list,
             hp_above=int, atk_above=int, rcv_above=int,
             hp_below=int, atk_below=int, rcv_below=int),
    185: Map(LS.ExtendedBoost, move_time_extend=int, elements=orb_list,
             types=type_list, hp=int, atk=int, rcv=int),
    186: Map(LS.Board7x6, elements=orb_list, types=type_list, hp=int, atk=int,
             rcv=int),
    # xyzを同時にn個以上つなげて消す
    192: Map(LS.ConnectedOrbsAll, orbs=orb_list, size=int, atk=int,
             combo_increase=int),
    # 5個L字消し
    193: Map(LS.LShape, orbs=orb_list, atk=int, rcv=int, dr=int),
    194: Map(LS.Rainbow, orbs=orb_list, color_min=int, atk=int,
             combo_increase=int),
    197: Map(LS.PoisonImmune),
    # 回復ドロップでx以上回復すると、ダメージを半減
    198: Map(LS.HealAbove, threshold=int, atk=int, dr=int, awoken_bind=int),
    # x色以上同時攻撃で固定yダメージ
    199: Map(LS.Rainbow, orbs=orb_list, color_min=int, fixed_extra_attack=int),
    # ドロップをx個以上つなげて消すと固定yダメージ
    200: Map(LS.ConnectedOrbs, orbs=orb_list, size=int, fixed_extra_attack=int),
    # [1, 1, 1, 0, 3, 1000000] -> 火の3コンボ以上で固定100万ダメージ
    # TODO: need more use case
    201: Map(LS.ElementCombo, combo_list=[orb_list] * 3, _=Unused(0), combo_min=int,
             fixed_extra_attack=int),
    # ドット進化のみでチーム
    203: Map(LS.EvoTeamStatBoost, evo_flag=int, hp=int, atk=int, rcv=int),
}

_ES_EFFECT_MAP = {
    71: Map(ES.VoidDamageShield, duration=int, unused=Unused(31, 1055),
            threshold=int),
    72: Map(ES.ElementDamageReduction, elements=orb_list, dr=int),
    83: Map(ES.SkillSetES, skill_ids=[int] * 10),
    118: Map(ES.TypeDamageReduction, types=type_list, dr=int),
}

def parse(skill_type: int, args: List[int]) -> SkillEffectTag:
    if skill_type == 129 and args == [8, 0, 100]:
        # This is the most common dummy type, includes:
        # モンスター経験値アップ
        # 売却
        # 潜在覚醒
        # 交換用
        # 希石
        return LS.Dummy()
    if skill_type == 48 and args == [3, 100]:
        # 能力覚醒
        return LS.Dummy()
    if skill_type == 121 and args == []:
        # スキルレベルアップ
        return LS.Dummy()

    if skill_type in _AS_EFFECT_MAP:
        return _AS_EFFECT_MAP[skill_type](*args)
    return _LS_EFFECT_MAP[skill_type](*args)

def parse_enemy_skill(skill_type: int, args: List[int]) -> SkillEffectTag:
    return _ES_EFFECT_MAP[skill_type](*args)
