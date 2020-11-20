from dataclasses import dataclass, field, InitVar
import enum
from typing import List

from pad_data.common import Awakening, Orb, Type
from pad_data.skill import skill_effect, SkillEffectTag

class Target(enum.IntEnum):
    ALL = 0
    ONE = 1

@skill_effect
@dataclass
class RandomSkill:
    unused_skill_id: InitVar[List[int]]
    def __post_init__(self, unused_skill_id: List[int]) -> None:
        pass

@skill_effect
@dataclass
class Nuke:
    element: Orb
    target: Target
    leech: int = 0
    percentage: int = 0
    percentage_upper: int = 0 # upper bound for random damage
    value: int = 0
    ignore_def: bool = False
    repeat: int = 1
    def __post_init__(self) -> None:
        if self.percentage_upper:
            assert self.percentage <= self.percentage_upper
        else:
            self.percentage_upper = self.percentage
        assert self.percentage == 0 or self.value == 0
        assert not (self.element != Orb.NO_ORB and self.ignore_def)

@skill_effect
@dataclass
class AtkNuke(Nuke):
    hp_remain: int = 100

@skill_effect
@dataclass
class TeamElementAtkNuke(Nuke):
    base_elem: List[Orb] = field(default_factory=list)

@skill_effect
@dataclass
class TeamHpNuke(Nuke):
    pass

@skill_effect
@dataclass
class RemainingHpNuke(Nuke):
    pass

@skill_effect
@dataclass
class BaseBuff:
    duration: int

@skill_effect
@dataclass
class RandomDurationBuff(BaseBuff):
    duration_max: int
    def __post_init__(self) -> None:
        assert self.duration <= self.duration_max

@skill_effect
@dataclass
class ElementDamageBuff(BaseBuff):
    cond: List[Orb]
    percentage: int

@skill_effect
@dataclass
class TypeDamageBuff(BaseBuff):
    cond: List[Type]
    percentage: int

@skill_effect
@dataclass
class DamageBuffByAwakening(BaseBuff):
    awakenings: List[Awakening]
    percentage: int
    def __post_init__(self) -> None:
        self.awakenings = [Awakening(x) for x in self.awakenings if x != 0]

@skill_effect
@dataclass
class DefenseBuffByAwakening(BaseBuff):
    awakenings: List[Awakening]
    percentage: int
    def __post_init__(self) -> None:
        self.awakenings = [Awakening(x) for x in self.awakenings if x != 0]

@skill_effect
@dataclass
class HealByAwakening:
    # heal amount = awakening count * self rcv * percentage
    # TODO: verify the formula from
    #       No. 3066 Pepper 光
    #       No. 5682 電龍楽士・マルシス
    unused_duration: InitVar[int]
    awakenings: List[Awakening]
    percentage: int
    def __post_init__(self, unused_duration: int) -> None:
        assert unused_duration == 0
        self.awakenings = [Awakening(x) for x in self.awakenings if x != 0]

def awakening_based_skill(duration: int, awakenings: List[Awakening], mode: int,
                          percentage: int) -> SkillEffectTag:
    cls = [HealByAwakening, DamageBuffByAwakening, DefenseBuffByAwakening]
    if mode == 2:
        percentage -= 100
    return cls[mode - 1](duration, awakenings, percentage)

@skill_effect
@dataclass
class OrbRefresh:
    pass

@skill_effect
@dataclass
class TeamRcvBasedHeal:
    percentage: int

@skill_effect
@dataclass
class OrbChange:
    # from -> to, random convert if len(to) > 1
    from_: List[Orb]
    to: List[Orb]

@skill_effect
@dataclass
class DoubleOrbChange:
    # from1 -> to1, from2 -> to2
    from1: Orb
    to1: Orb
    from2: Orb
    to2: Orb

@skill_effect
@dataclass
class OrbEnhance:
    orbs: List[Orb]

@skill_effect
@dataclass
class RandomOrbSpawn:
    count: int
    orb: List[Orb]
    exclude: List[Orb]

@skill_effect
@dataclass
class RouletteSpawn:
    duration: int
    count: int


@skill_effect
@dataclass
class AllOrbChange:
    orbs: List[Orb]

@skill_effect
@dataclass
class BaseBoardChange:
    def orb_count(self) -> int:
        raise NotImplementedError

    @staticmethod
    def _popcount(x: int) -> int:
        ret = 0
        while x > 0:
            ret += 1
            x &= x - 1
        return ret

@skill_effect
@dataclass
class ColumnChange(BaseBoardChange):
    # pos: for 6x5, bit0 = left most column, bit5 = right most
    pos1: int
    orb1: List[Orb]
    pos2: int
    orb2: List[Orb]

    def __post_init__(self) -> None:
        # orbX and posX should be both zero or both non-zero
        assert not ((len(self.orb1) == 0) ^ (self.pos1 == 0))
        assert not ((len(self.orb2) == 0) ^ (self.pos2 == 0))

    def orb_count(self) -> int:
        return self._popcount(self.pos1) + self._popcount(self.pos2)

@skill_effect
@dataclass
class RowChange(BaseBoardChange):
    # pos: for 6x5, bit0 = top row, bit4 = bottom row
    pos1: int
    orb1: List[Orb]
    pos2: int
    orb2: List[Orb]

    def __post_init__(self) -> None:
        assert len(self.orb1) == (0 if self.pos1 == 0 else 1)
        assert len(self.orb2) == (0 if self.pos2 == 0 else 1)

    def orb_count(self) -> int:
        return self._popcount(self.pos1) + self._popcount(self.pos2)

@skill_effect
@dataclass
class BoardChange(BaseBoardChange):
    # 十字 / L字 etc 生成
    # row is a 5-element array representing top row to bottom row
    # for each element in row array, bit0 = left most column, bit5 = right most
    rows: List[int]
    orb: Orb

    def orb_count(self) -> int:
        return sum(self._popcount(x) for x in self.rows)

@skill_effect
@dataclass
class DefenseReduction(BaseBuff):
    percentage: int

@skill_effect
@dataclass
class DamageReduction(BaseBuff):
    percentage: int

@skill_effect
@dataclass
class ElementDamageReduction(BaseBuff):
    element: Orb
    percentage: int

@skill_effect
@dataclass
class DelayEnemyAttack:
    duration: int
    unused: InitVar[int]
    def __post_init__(self, unused: int) -> None:
        assert unused == 0 or unused == self.duration

@skill_effect
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
    def __post_init__(self) -> None:
        heals = [self.rcv_percentage, self.hp_value, self.hp_percentage]
        assert len([x for x in heals if x > 0]) <= 1

@skill_effect
@dataclass
class HealOverTime(BaseBuff, Heal):
    def __post_init__(self) -> None:
        super().__post_init__()
        assert self.rcv_percentage == 0
        assert self.hp_value == 0

@skill_effect
@dataclass
class Poison:
    percentage: int

@skill_effect
@dataclass
class ChangeTheWorld:
    second: int

@skill_effect
@dataclass
class MoveTimeExtend(BaseBuff):
    decisecond: int
    percentage: int
    def __post_init__(self) -> None:
        assert not (self.decisecond > 0 and self.percentage > 0)

@skill_effect
@dataclass
class SkillBind(BaseBuff):
    pass

@skill_effect
@dataclass
class Gravity:
    percentage: int

@skill_effect
@dataclass
class TrueGravity:
    # 敵の最大HPx％分のダメージ
    percentage: int

@skill_effect
@dataclass
class Skyfall(RandomDurationBuff):
    orbs: List[Orb]
    percentage: int

@skill_effect
@dataclass
class SkyfallEnhancedOrbs(BaseBuff):
    percentage: int

@skill_effect
@dataclass
class SkyfallLockedOrbs(BaseBuff):
    orbs: List[Orb]

@skill_effect
@dataclass
class NoSkyfall(BaseBuff):
    pass

@skill_effect
@dataclass
class IgnoreAbsorb(BaseBuff):
    element: bool
    damage: bool

@skill_effect
@dataclass
class ReduceCooldown:
    turn: List[int]
    def __post_init__(self) -> None:
        assert self.turn[0] <= self.turn[1]

@skill_effect
@dataclass
class LeaderSwap:
    pass

@skill_effect
@dataclass
class SelfElementChange(BaseBuff):
    element: Orb

@skill_effect
@dataclass
class EnemyElementChange:
    element: Orb

@skill_effect
@dataclass
class ComboIncrease(BaseBuff):
    combo: int

@skill_effect
@dataclass
class Unlock:
    pass

@skill_effect
@dataclass
class Lock:
    orbs: List[Orb]
    count: int  # number of maximum locked orbs, usually 42 or 99

@skill_effect
@dataclass
class Cleave(BaseBuff):
    # xターンの間、攻撃が全体攻撃になる
    pass

@skill_effect
@dataclass
class Counter(BaseBuff):
    percentage: int
    element: Orb

@skill_effect
@dataclass
class ComboHelper:
    # 3コンボ分のルートを表示
    pass

@skill_effect
@dataclass
class VoidDamagePiercer(BaseBuff):
    pass

@skill_effect
@dataclass
class Sacrifice:
    hp_remain: int

@skill_effect
@dataclass
class UnmatchableRecover:
    # 消せないドロップ状態をnターン回復
    turn: int

@skill_effect
@dataclass
class Transform:
    to: int

@skill_effect
@dataclass
class SkillSet:
    skill_ids: List[int]
