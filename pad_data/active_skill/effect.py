from dataclasses import dataclass, field, InitVar
import enum
from typing import List

from pad_data.common import Awakening, Orb, Type

class Target(enum.IntEnum):
    ALL = 0
    ONE = 1

@dataclass
class RandomSkill:
    unused_skill_id: InitVar[List[int]]
    def __post_init__(self, unused_skill_id):
        pass

@dataclass
class Nuke:
    element: Orb
    target: Target
    leech: int = 0
    percentage: List[int] = field(default_factory=lambda: [0, 0])
    value: int = 0
    ignore_def: bool = False
    repeat: int = 1
    def __post_init__(self):
        if isinstance(self.percentage, int):
            self.percentage = [self.percentage, self.percentage]
        assert self.percentage[0] <= self.percentage[1]
        assert self.percentage == [0, 0] or self.value == 0
        assert not (self.element != Orb.NO_ORB and self.ignore_def)

@dataclass
class AtkNuke(Nuke):
    hp_remain: int = 100

@dataclass
class AtkNukeType2(AtkNuke):
    unused: InitVar[int] = 0
    # pylint: disable=arguments-differ
    def __post_init__(self, unused):
        super().__post_init__()
        # percentage of skill type 2 may be one or two int...
        assert unused == 0 or unused == self.percentage[0]

@dataclass
class TeamElementAtkNuke(Nuke):
    base_elem: List[Orb] = field(default_factory=list)

@dataclass
class TeamHpNuke(Nuke):
    pass

@dataclass
class RemainingHpNuke(Nuke):
    pass

@dataclass
class BaseBuff:
    duration: int

@dataclass
class ElementDamageBuff(BaseBuff):
    cond: List[Orb]
    percentage: int

@dataclass
class TypeDamageBuff(BaseBuff):
    cond: List[Type]
    percentage: int

@dataclass
class DamageBuffByAwakening(BaseBuff):
    awakenings: List[Awakening]
    percentage: int
    def __post_init__(self):
        self.awakenings = [Awakening(x) for x in self.awakenings if x != 0]

@dataclass
class DefenseBuffByAwakening(BaseBuff):
    awakenings: List[Awakening]
    percentage: int
    def __post_init__(self):
        self.awakenings = [Awakening(x) for x in self.awakenings if x != 0]

@dataclass
class HealByAwakening:
    # heal amount = awakening count * self rcv * percentage
    # TODO: verify the formula from
    #       No. 3066 Pepper 光
    #       No. 5682 電龍楽士・マルシス
    unused_duration: InitVar[int]
    awakenings: List[Awakening]
    percentage: int
    def __post_init__(self, unused_duration):
        assert unused_duration == 0
        self.awakenings = [Awakening(x) for x in self.awakenings if x != 0]

def awakening_based_skill(duration, awakenings, mode, percentage):
    cls = [None, HealByAwakening, DamageBuffByAwakening, DefenseBuffByAwakening]
    if mode == 2:
        percentage -= 100
    return cls[mode](duration, awakenings, percentage)

@dataclass
class OrbRefresh:
    pass

@dataclass
class TeamRcvBasedHeal:
    percentage: int

@dataclass
class OrbChange:
    # from -> to, random convert if len(to) > 1
    from_: List[Orb]
    to: List[Orb]

@dataclass
class DoubleOrbChange:
    # from1 -> to1, from2 -> to2
    from1: Orb
    to1: Orb
    from2: Orb
    to2: Orb

@dataclass
class OrbEnhance:
    orbs: List[Orb]

@dataclass
class RandomOrbSpawn:
    count: int
    orb: List[Orb]
    exclude: List[Orb]

@dataclass
class AllOrbChange:
    orbs: List[Orb]

@dataclass
class BaseBoardChange:
    def orb_count(self):
        raise NotImplementedError

    @staticmethod
    def _popcount(x):
        ret = 0
        while x > 0:
            ret += 1
            x &= x - 1
        return ret

@dataclass
class ColumnChange(BaseBoardChange):
    # pos: for 6x5, bit0 = left most column, bit5 = right most
    pos1: int
    orb1: List[Orb]
    pos2: int
    orb2: List[Orb]

    def __post_init__(self):
        assert len(self.orb1) == (0 if self.pos1 == 0 else 1)
        assert len(self.orb2) == (0 if self.pos2 == 0 else 1)

    def orb_count(self):
        return self._popcount(self.pos1) + self._popcount(self.pos2)

@dataclass
class RowChange(BaseBoardChange):
    # pos: for 6x5, bit0 = top row, bit4 = bottom row
    pos1: int
    orb1: List[Orb]
    pos2: int
    orb2: List[Orb]

    def __post_init__(self):
        assert len(self.orb1) == (0 if self.pos1 == 0 else 1)
        assert len(self.orb2) == (0 if self.pos2 == 0 else 1)

    def orb_count(self):
        return self._popcount(self.pos1) + self._popcount(self.pos2)

@dataclass
class BoardChange(BaseBoardChange):
    # 十字 / L字 etc 生成
    # row is a 5-element array representing top row to bottom row
    # for each element in row array, bit0 = left most column, bit5 = right most
    rows: List[int]
    orb: Orb

    def orb_count(self):
        return sum(self._popcount(x) for x in self.rows)

@dataclass
class DefenseReduction(BaseBuff):
    percentage: int

@dataclass
class DamageReduction(BaseBuff):
    percentage: int

@dataclass
class ElementDamageReduction(BaseBuff):
    element: Orb
    percentage: int

@dataclass
class DelayEnemyAttack:
    duration: int
    unused: InitVar[int]
    def __post_init__(self, unused):
        assert unused == 0 or unused == self.duration

@dataclass
class Heal:
    # バインド状態をnターン回復
    bind: int
    # 回復力n倍のHP回復
    rcv_percentage: int
    # HPをn回復
    hp_value: int
    # HPn%回復
    hp_percentage: int
    # 覚醒無効状態をnターン回復
    awoken_bind: int
    def __post_init__(self):
        heals = [self.rcv_percentage, self.hp_value, self.hp_percentage]
        assert len([x for x in heals if x > 0]) <= 1

@dataclass
class HealOverTime(BaseBuff, Heal):
    unused: InitVar[int]
    # pylint: disable=arguments-differ
    def __post_init__(self, unused):
        super().__post_init__()
        assert unused == 0
        assert self.rcv_percentage == 0
        assert self.hp_value == 0

@dataclass
class Poison:
    percentage: int

@dataclass
class ChangeTheWorld:
    second: int

@dataclass
class MoveTimeExtend(BaseBuff):
    decisecond: int
    percentage: int
    def __post_init__(self):
        assert not (self.decisecond > 0 and self.percentage > 0)

@dataclass
class Gravity:
    percentage: int

@dataclass
class TrueGravity:
    # 敵の最大HPx％分のダメージ
    percentage: int

@dataclass
class Skyfall(BaseBuff):
    orbs: List[Orb]
    percentage: int
    unused: InitVar[int] = None
    def __post_init__(self, unused):
        assert unused == self.duration

@dataclass
class SkyfallEnhancedOrbs(BaseBuff):
    percentage: int

@dataclass
class NoSkyfall(BaseBuff):
    pass

@dataclass
class IgnoreAbsorb(BaseBuff):
    element: bool
    damage: bool

@dataclass
class ReduceCooldown:
    turn: (int, int)
    def __post_init__(self):
        assert self.turn[0] <= self.turn[1]

@dataclass
class LeaderSwap:
    pass

@dataclass
class SelfElementChange(BaseBuff):
    element: Orb

@dataclass
class EnemyElementChange:
    element: Orb

@dataclass
class ComboIncrease(BaseBuff):
    combo: int

@dataclass
class Unlock:
    pass

@dataclass
class Lock:
    orbs: List[Orb]
    unused: InitVar[int]
    def __post_init__(self, unused):
        assert unused == 42 or unused == 99

@dataclass
class Cleave(BaseBuff):
    # xターンの間、攻撃が全体攻撃になる
    pass

@dataclass
class Counter(BaseBuff):
    percentage: int
    element: Orb

@dataclass
class ComboHelper:
    # 3コンボ分のルートを表示
    pass

@dataclass
class VoidDamagePiercer(BaseBuff):
    pass

@dataclass
class Sacrifice:
    hp_remain: int

@dataclass
class UnmatchableRecover:
    # 消せないドロップ状態をnターン回復
    turn: int

@dataclass
class Transform:
    to: int

@dataclass
class SkillSet:
    skill_ids: List[int]
