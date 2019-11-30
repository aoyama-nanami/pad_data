from dataclasses import dataclass, field, InitVar
from typing import ClassVar, List

from pad_data import common

@dataclass
class BaseStatBoost:
    elements: List[common.Orb] = field(default_factory=list)
    types: List[common.Type] = field(default_factory=list)
    hp: int = 0
    atk: int = 0
    rcv: int = 0

    dr_elements: List[common.Orb] = field(default_factory=list)
    dr: int = 0

    ALL_ELEM: ClassVar[common.Orb] = [
        common.Orb.FIRE, common.Orb.WATER, common.Orb.WOOD,
        common.Orb.LIGHT, common.Orb.DARK]

    def __post_init__(self):
        if self.elements == [] and self.types == []:
            self.elements = BaseStatBoost.ALL_ELEM
        if self.dr > 0 and self.dr_elements == []:
            self.dr_elements = BaseStatBoost.ALL_ELEM

    def calculate_atk(self, combos, trigger=False, hp=100):
        raise NotImplementedError

    def effective_hp(self):
        ret = 1
        if self.dr:
            ret /= (1 - self.dr / 100)
        if self.hp:
            ret *= self.hp / 100
        return ret

@dataclass
class SteppedStatBoost(BaseStatBoost):
    atk_step: int = 0
    rcv_step: int = 0

    def max_step(self):
        raise NotImplementedError

def by_stat_id(cls):
    def func(stat_id_list, percentage, **kwargs):
        for stat_id in stat_id_list:
            assert 0 <= stat_id <= 2
            if stat_id == 1:
                kwargs['atk'] = percentage
            elif stat_id == 2:
                kwargs['rcv'] = percentage
        return cls(**kwargs)
    return func

@dataclass
class ExtraBuff:
    move_time_extend: int = 0 # unit is 1/100 sec
    combo_increase: int = 0
    fixed_extra_attack: int = 0
    awoken_bind: int = 0

# conditions

@dataclass
class StatBoost(BaseStatBoost):
    pass

@dataclass
class ExtendedBoost(BaseStatBoost, ExtraBuff):
    pass

@dataclass
class HpAbove(BaseStatBoost):
    proc_rate: int = 100
    hp_above: int = 0

@dataclass
class HpBelow(BaseStatBoost):
    proc_rate: int = 100
    hp_below: int = 0

@dataclass
class Combo(SteppedStatBoost):
    combo: int = 0
    combo_max: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.combo_max == 0:
            self.combo_max = self.combo

    def calculate_atk(self, combos, trigger=False, hp=100):
        c = min(len(combos), self.combo_max)
        if c < self.combo:
            return None
        return self.atk + (self.combo_max - c) * self.atk_step

    def max_step(self):
        return self.combo_max - self.combo

@dataclass
class ComboExact(BaseStatBoost):
    combo: int = 0

@dataclass
class Rainbow(SteppedStatBoost, ExtraBuff):
    orbs: List[common.Orb] = field(default_factory=list)
    color_min: int = 0
    color_max: int = field(init=False)

    color_step: InitVar[int] = 0

    # pylint: disable=arguments-differ
    def __post_init__(self, color_step):
        super().__post_init__()

        if color_step == 0:
            self.color_max = self.color_min
        else:
            self.color_max = min(self.color_min + color_step, len(self.orbs))

    def max_step(self):
        return self.color_max - self.color_min

@dataclass
class ElementCombo(SteppedStatBoost, ExtraBuff):
    combos: List[List[common.Orb]] = field(default_factory=list)
    combo_min: int = 0

    def __post_init__(self):
        super().__post_init__()

        self.combos = list(filter(lambda x: x, self.combos))
        # pylint: disable=not-an-iterable
        assert all(len(c) <= 1 for c in self.combos)
        # pylint: disable=not-an-iterable
        assert len(self.combos) >= self.combo_min

    def max_step(self):
        return len(self.combos) - self.combo_min

@dataclass
class ConnectedOrbs(SteppedStatBoost, ExtraBuff):
    # xyzをn個以上つなげて消す
    # triggers if any matched
    orbs: List[common.Orb] = field(default_factory=list)
    size: int = 0
    size_max: int = 0

    def max_step(self):
        return self.size_max - self.size

@dataclass
class ConnectedOrbsAll(BaseStatBoost, ExtraBuff):
    # xyzを"同時"にn個以上つなげて消す
    # triggers if all matched
    orbs: List[common.Orb] = field(default_factory=list)
    size: int = 0

@dataclass
class HeartCross(BaseStatBoost):
    pass

@dataclass
class Trigger(BaseStatBoost):
    def calculate_atk(self, combos, trigger=False, hp=100):
        return self.atk if trigger else None

@dataclass
class EnhancedOrbs5(BaseStatBoost):
    pass

@dataclass
class MultiplayerGame(BaseStatBoost):
    pass

@dataclass
class NoSkyfallLS(BaseStatBoost):
    pass

@dataclass
class MatchFourOrAbove(BaseStatBoost):
    # ドロップをn個以下で消せない
    match: int = 0

@dataclass
class LShape(BaseStatBoost):
    orbs: List[common.Orb] = field(default_factory=list)

    def calculate_atk(self, combos, trigger=False, hp=100):
        for c in combos:
            if c.shape == common.Shape.L and c.orb in self.orbs:
                return self.atk
        return None

@dataclass
class Board7x6(BaseStatBoost):
    pass

@dataclass
class OrbRemaining(NoSkyfallLS, SteppedStatBoost):
    # パズル後の残りドロップ数がn個以下
    threshold: int = 0

    def max_step(self):
        return self.threshold

@dataclass
class FixedMovementTime(BaseStatBoost):
    # 操作時間n秒固定
    seconds: int = 0

@dataclass
class TeamStatBoost(BaseStatBoost):
    card_ids: List[int] = field(default_factory=list)

@dataclass
class CollaboTeamStatBoost(BaseStatBoost):
    collabo_ids: List[int] = field(default_factory=list)

@dataclass
class HealAbove(BaseStatBoost, ExtraBuff):
    threshold: int = 0

# end condition

@dataclass
class CrossAtkBoost:
    args: InitVar[List[int]]
    atk_table: List[int] = field(init=False)
    def __post_init__(self, args):
        self.atk_table = [0] * 10
        for (o, atk) in args:
            if atk:
                self.atk_table[o] = atk

def hp_cond_139(elements, types, spec):
    # tuple[0]: hp condition
    #      [1]: 0=above, 1=below
    #      [2]: atk
    def conv(s):
        if s[1] == 0:
            return HpAbove(elements=elements, types=types, hp_above=s[0],
                           atk=s[2])
        return HpBelow(elements=elements, types=types, hp_below=s[0], atk=s[2])
    return [conv(s) for s in spec if s[0]]

# pylint: disable=too-many-arguments
def hp_cond_183(elements, types, hp_above, atk_above, rcv_above, hp_below,
                atk_below, rcv_below):
    res = []
    if hp_above:
        res.append(HpAbove(elements=elements, types=types, hp_above=hp_above,
                           atk=atk_above, rcv=rcv_above))
    if hp_below:
        res.append(HpBelow(elements=elements, types=types, hp_below=hp_below,
                           atk=atk_below, rcv=rcv_below))
    return res

def double_stat_boost(params_0, params_1):
    # param = [elements, types, hp, atk, rcv]
    return [
        StatBoost(elements=p[0], types=p[1], hp=p[2], atk=p[3], rcv=p[4])
        for p in [params_0, params_1]
    ]

@dataclass
class Resolve: # 根性
    hp_threshold: int

@dataclass
class CounterLS:
    proc_rate: int
    atk: int
    orb: common.Orb

@dataclass
class ExtraAttack:
    atk: int

@dataclass
class ExtraHeal:
    rcv: int

@dataclass
class TaikoNoise:
    pass

@dataclass
class Dummy:
    # モンスター経験値アップ, 覚醒スキル解放 etc
    pass

@dataclass
class RankExpUp:
    percentage: int

@dataclass
class GoldLootUp:
    percentage: int

@dataclass
class TreasureLootUp:
    percentage: int

@dataclass
class PoisonImmune:
    pass

@dataclass
class SkillSetLS:
    skill_ids: List[int]
