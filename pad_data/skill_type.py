import copy
import functools
import itertools

from pad_data.common import Orb, Type
from pad_data.effect import *

# special skill type for combined skill effect
MULTI_EFFECT_ID = 116

def _consume_all_args(func, end):
    def inner(func, end, it):
        return [func(x) for x in itertools.takewhile(lambda x: x > end, it)]
    return functools.partial(inner, func, end)

class Map:
    def __init__(self, cls, **kwargs):
        self._cls = cls
        self._kwargs = kwargs

    def __call__(self, *args):
        kwargs = copy.deepcopy(self._kwargs)

        args_iter = iter(args)
        g = itertools.chain(args_iter, itertools.repeat(0))
        def convert(x):
            if isinstance(x, list):
                return list(map(convert, x))
            if isinstance(x, functools.partial):
                return x(g)
            if callable(x):
                return x(next(g))
            return x

        obj = self._cls(**{k: convert(v) for k, v in kwargs.items()})

        try:
            next(args_iter)
            assert False, 'args not fully consumed!'
        except StopIteration:
            pass

        return obj

_EFFECT_MAP = {
    0: Map(AtkNuke, element=Orb, percentage=int, target=Target.ALL),
    1: Map(AtkNuke, element=Orb, value=int, target=Target.ALL),
    2: Map(AtkNukeType2, element=Orb.NO_ORB, percentage=int,
           target=Target.ONE, unused=int),
    3: Map(DamageReduction, duration=int, percentage=int),
    4: Map(Poison, percentage=int),
    5: Map(ChangeTheWorld, second=int),
    6: Map(Gravity, percentage=int),
    7: Map(RcvBasedHeal, percentage=int),
    8: Map(FixedHeal, value=int),
    9: Map(OrbChange, from_=[Orb], to=[Orb]),
    10: Map(OrbRefresh),
    18: Map(DelayEnemyAttack, duration=int, unused=int),
    19: Map(DefenseReduction, duration=int, percentage=int),
    20: Map(DoubleOrbChange, from1=Orb, to1=Orb, from2=Orb, to2=Orb),
    21: Map(ElementDamageReduction, duration=int, element=Orb,
            percentage=int),
    35: Map(AtkNuke, element=Orb.NO_ORB, percentage=int, leech=int,
            target=Target.ONE),
    37: Map(AtkNuke, element=Orb, percentage=int, target=Target.ONE),
    42: Map(AtkNuke, target=Orb, element=Orb, value=int),
    50: Map(DamageBuff, duration=int, cond=[Orb], percentage=int),
    51: Map(Cleave, duration=int),
    52: Map(OrbEnhance, orbs=[Orb], unused=int),
    55: Map(AtkNuke, target=Target.ONE, element=Orb.NO_ORB,
            ignore_def=True, value=int),
    56: Map(AtkNuke, target=Target.ALL, element=Orb.NO_ORB,
            ignore_def=True, value=int),
    58: Map(AtkNuke, target=Target.ALL, element=Orb,
            percentage=[int, int]),
    59: Map(AtkNuke, target=Target.ONE, element=Orb,
            percentage=[int, int]),
    60: Map(Counter, duration=int, percentage=int, element=Orb),
    71: Map(AllOrbChange, orbs=_consume_all_args(Orb, -1)),
    84: Map(AtkNuke, target=Target.ONE, element=Orb,
            percentage=[int, int], hp_remain=int),
    85: Map(AtkNuke, target=Target.ONE, element=Orb,
            percentage=[int, int], hp_remain=int),
    86: Map(FixedValueNuke, element=Orb, value=int, unused=int,
            hp_remain=int, target=Target.ONE),
    87: Map(FixedValueNuke, element=Orb, value=int, unused=int,
            hp_remain=int, target=Target.ALL),
    88: Map(DamageBuff, duration=int, cond=[Type], percentage=int),
    90: Map(DamageBuff, duration=int, cond=[Orb, Orb], percentage=int),
    91: Map(OrbEnhance, orbs=[Orb, Orb], unused=int),
    92: Map(DamageBuff, duration=int, cond=[Type, Type], percentage=int),
    93: Map(LeaderSwap),
    110: Map(RemainingHpNuke, target=Target, element=Orb,
             percentage=[int, int], unused=int),
    115: Map(AtkNuke, target=Target.ONE, element=Orb, percentage=int,
             leech=int),
    117: Map(Recovery, bind=int, rcv_percentage=int, hp_value=int,
             hp_percentage=int, awoken_bind=int),
    118: Map(RandomSkill, unused_skill_id=_consume_all_args(int, 0)),
    126: Map(Skyfall, orbs=orb_list, duration=int, unused=int, percentage=int),
    127: Map(ColumnChange, pos1=int, orb1=orb_list, pos2=int, orb2=orb_list),
    128: Map(RowChange, pos1=int, orb1=orb_list, pos2=int, orb2=orb_list),
    132: Map(MoveTimeExtend, duration=int, decisecond=int, percentage=int),
    140: Map(OrbEnhance, orbs=orb_list, unused=int),
    141: Map(RandomOrbSpawn, count=int, orb=orb_list, exclude=orb_list),
    142: Map(SelfElementChange, duration=int, element=Orb),
    143: Map(TeamHpNuke, percentage=int, element=Orb,
             target=Target.ALL),
    144: Map(TeamElementAtkNuke, base_elem=orb_list, percentage=int,
             target=Target, element=Orb),
    145: Map(TeamRcvBasedHeal, percentage=int),
    146: Map(ReduceCooldown, turn=[int, int]),
    152: Map(Lock, orbs=orb_list, unused=int),
    153: Map(EnemyElementChange, element=Orb, unused=int),
    154: Map(OrbChange, from_=orb_list, to=orb_list),
    156: Map(awakening_based_skill, duration=int, awakenings=[int, int, int],
             mode=int, percentage=int),
    160: Map(ComboIncrease, duration=int, combo=int),
    161: Map(TrueGravity, percentage=int),
    172: Map(Unlock),
    173: Map(IgnoreAbsorb, duration=int, element_absorb=bool, unused=int,
             damage_absorb=int),
    176: Map(BoardChange, rows=[int, int, int, int, int], orb=Orb),
    179: Map(RecoveryOverTime, duration=int, unused=int, hp_percentage=int,
             bind=int, awoken_bind=int, rcv_percentage=0, hp_value=0),
    180: Map(SkyfallEnhancedOrbs, duration=int, percentage=int),
    184: Map(NoSkyfall, duration=int),
    # 敵1体に N の固定ダメージ x M 回, represented by array of M following item.
    188: Map(AtkNuke, target=Target.ONE, element=Orb.NO_ORB,
             ignore_def=True, value=int),
    189: Map(ComboHelper),
    191: Map(VoidDamagePiercer, duration=int),
}

def parse(skill_type, args):
    return _EFFECT_MAP[skill_type](*args)
