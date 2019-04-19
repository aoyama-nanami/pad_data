import copy
import functools
import itertools

from .common import Element, Orb, Type
from .effect import *

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
            elif isinstance(x, functools.partial):
                return x(g)
            elif callable(x):
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
    0: Map(AtkBasedDamage, element=Element, percentage=int, target=Target.ALL),
    1: Map(FixedValueDamage, element=Element, value=int, target=Target.ALL),
    2: Map(AtkBasedDamage, element=Element.NO_ELEMENT, percentage=int,
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
    21: Map(ElementDamageReduction, duration=int, element=Element,
            percentage=int),
    35: Map(AtkBasedDamage, element=Element.NO_ELEMENT, percentage=int,
            leech=int, target=Target.ONE),
    37: Map(AtkBasedDamage, element=Element, percentage=int, target=Target.ONE),
    42: Map(FixedValueDamage, target=Element, element=Element, value=int),
    50: Map(DamageBuff, duration=int, cond=[Orb], percentage=int),
    51: Map(Cleave, duration=int),
    52: Map(OrbEnhance, orbs=[Orb], unused=int),
    55: Map(FixedValueDamage, target=Target.ONE, element=Element.NO_ELEMENT,
            ignore_def=True, value=int),
    56: Map(FixedValueDamage, target=Target.ALL, element=Element.NO_ELEMENT,
            ignore_def=True, value=int),
    58: Map(AtkBasedDamage, target=Target.ALL, element=Element,
            percentage=[int, int]),
    59: Map(AtkBasedDamage, target=Target.ONE, element=Element,
            percentage=[int, int]),
    60: Map(Counter, duration=int, percentage=int, element=Element),
    71: Map(AllOrbChange, orbs=_consume_all_args(Orb, -1)),
    84: Map(AtkBasedDamage, target=Target.ONE, element=Element,
            percentage=[int, int], hp_remain=int),
    85: Map(AtkBasedDamage, target=Target.ONE, element=Element,
            percentage=[int, int], hp_remain=int),
    86: Map(FixedValueDamage, element=Element, value=int, unused=int,
            hp_remain=int, target=Target.ONE),
    87: Map(FixedValueDamage, element=Element, value=int, unused=int,
            hp_remain=int, target=Target.ALL),
    88: Map(DamageBuff, duration=int, cond=[Type], percentage=int),
    90: Map(DamageBuff, duration=int, cond=[Orb, Orb], percentage=int),
    91: Map(OrbEnhance, orbs=[Orb, Orb], unused=int),
    92: Map(DamageBuff, duration=int, cond=[Type, Type], percentage=int),
    93: Map(LeaderSwap),
    110: Map(RemainHpBasedDamage, target=Target, element=Element,
             percentage=[int, int], unused=int),
    115: Map(AtkBasedDamage, target=Target.ONE, element=Element, percentage=int,
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
    142: Map(SelfElementChange, duration=int, element=Element),
    143: Map(TeamHpBasedDamage, percentage=int, element=Element,
             target=Target.ALL),
    144: Map(TeamAtkBasedDamage, base_elem=element_list, percentage=int,
             target=Target, element=Element),
    145: Map(TeamRcvBasedHeal, percentage=int),
    146: Map(ReduceCooldown, turn=[int, int]),
    152: Map(Lock, orbs=orb_list, unused=int),
    153: Map(EnemyElementChange, element=Element, unused=int),
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
    188: Map(FixedValueDamage, target=Target.ONE, element=Element.NO_ELEMENT,
             ignore_def=True, value=int),
    189: Map(ComboHelper),
    191: Map(VoidDamagePiercer, duration=int),
}

def parse_skill_effect(skill_type, args):
    return _EFFECT_MAP[skill_type](*args)
