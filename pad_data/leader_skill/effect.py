from collections import Counter
from dataclasses import dataclass, field, InitVar
from typing import Any, Callable, ClassVar, final, List, Optional, Tuple
from typing import TypeVar

from pad_data.common import CCombo, Orb, Type, Shape
from pad_data.skill import skill_effect, SkillEffectTag

T = TypeVar('T', bound=SkillEffectTag)


@skill_effect
@dataclass
class BaseStatBoost:
    elements: List[Orb] = field(default_factory=list)
    types: List[Type] = field(default_factory=list)
    hp: int = 0
    atk: int = 0
    rcv: int = 0

    dr_elements: List[Orb] = field(default_factory=list)
    dr: int = 0

    ALL_ELEM: ClassVar[List[Orb]] = [
        Orb.FIRE, Orb.WATER, Orb.WOOD, Orb.LIGHT, Orb.DARK]

    def __post_init__(self) -> None:
        if self.elements == [] and self.types == []:
            self.elements = BaseStatBoost.ALL_ELEM
        if self.dr > 0 and self.dr_elements == []:
            self.dr_elements = BaseStatBoost.ALL_ELEM

    # return value in unit 1/100
    def calculate_atk(self, combos: List[CCombo], trigger: bool=False,
                      hp: int=100) -> Optional[int]:
        raise NotImplementedError

    def effective_hp(self) -> float:
        ret = 1.0
        if self.dr:
            ret /= (1 - self.dr / 100)
        if self.hp:
            ret *= self.hp / 100
        return ret

@skill_effect
@dataclass
class SteppedStatBoost(BaseStatBoost):
    atk_step: int = 0
    rcv_step: int = 0

    def max_step(self) -> int:
        raise NotImplementedError

def by_stat_id(cls: Callable[..., T]) -> Callable[..., T]:
    def func(stat_id_list: List[int], percentage: int, **kwargs: Any
             ) -> T:
        for stat_id in stat_id_list:
            assert 0 <= stat_id <= 2
            if stat_id == 1:
                kwargs['atk'] = percentage
            elif stat_id == 2:
                kwargs['rcv'] = percentage
        return cls(**kwargs)
    return func

@skill_effect
@dataclass
class ExtraBuff:
    move_time_extend: int = 0 # unit is 1/100 sec
    combo_increase: int = 0
    fixed_extra_attack: int = 0
    awoken_bind: int = 0

@skill_effect
@dataclass
class MultiEffect:
    items: List[SkillEffectTag]

# conditions

# add @final to prevent inhereint from this accidentally
@final
@skill_effect
@dataclass
class StatBoost(BaseStatBoost):
    def calculate_atk(self, combos: List[CCombo], trigger: bool=False,
                      hp: int=100) -> Optional[int]:
        return self.atk

@final
@skill_effect
@dataclass
class ExtendedBoost(BaseStatBoost, ExtraBuff):
    def calculate_atk(self, combos: List[CCombo], trigger: bool=False,
                      hp: int=100) -> Optional[int]:
        return self.atk

@skill_effect
@dataclass
class HpAbove(BaseStatBoost):
    proc_rate: int = 100
    hp_above: int = 0

@skill_effect
@dataclass
class HpBelow(BaseStatBoost):
    proc_rate: int = 100
    hp_below: int = 0

@skill_effect
@dataclass
class Combo(SteppedStatBoost):
    combo: int = 0
    combo_max: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.combo_max == 0:
            self.combo_max = self.combo

    def calculate_atk(self, combos: List[CCombo], trigger: bool=False,
                      hp: int=100) -> Optional[int]:
        c = min(len(combos), self.combo_max)
        if c < self.combo:
            return None
        return self.atk + (self.combo_max - c) * self.atk_step

    def max_step(self) -> int:
        return self.combo_max - self.combo

@skill_effect
@dataclass
class ComboExact(BaseStatBoost):
    combo: int = 0

@skill_effect
@dataclass
class Rainbow(SteppedStatBoost, ExtraBuff):
    orbs: List[Orb] = field(default_factory=list)
    color_min: int = 0
    color_max: int = field(init=False)

    color_step: InitVar[int] = 0

    # pylint: disable=arguments-differ
    def __post_init__(self, color_step: int) -> None: # type: ignore[override]
        super().__post_init__()

        if color_step == 0:
            self.color_max = self.color_min
        else:
            self.color_max = min(self.color_min + color_step, len(self.orbs))

    def max_step(self) -> int:
        return self.color_max - self.color_min

    def calculate_atk(self, combos: List[CCombo], trigger: bool=False,
                      hp: int=100) -> Optional[int]:
        combo_colors = set(c.orb for c in combos)
        color_matched = len(combo_colors.intersection(set(self.orbs)))
        color_matched = min(color_matched, self.color_max)
        if color_matched < self.color_min:
            return None
        return self.atk + (color_matched - self.color_min) * self.atk_step

@skill_effect
@dataclass
class ElementCombo(SteppedStatBoost, ExtraBuff):
    combo_list: InitVar[List[List[Orb]]] = field(default=None)
    combos: List[Orb] = field(init=False)
    combo_min: int = 0

    # pylint: disable=arguments-differ
    def __post_init__(self, # type: ignore[override]
                      combo_list: List[List[Orb]]) -> None:
        super().__post_init__()

        # pylint: disable=not-an-iterable
        assert all(len(c) <= 1 for c in combo_list)
        self.combos = [c[0] for c in combo_list if len(c)]
        # pylint: disable=not-an-iterable
        assert len(self.combos) >= self.combo_min

    def max_step(self) -> int:
        return len(self.combos) - self.combo_min

    def calculate_atk(self, combos: List[CCombo], trigger: bool=False,
                      hp: int=100) -> Optional[int]:
        set1 = Counter(self.combos)
        set2 = Counter(c.orb for c in combos)
        c = sum((set1 & set2).values())
        if c < self.combo_min:
            return None
        return self.atk + self.atk_step * (c - self.combo_min)

@skill_effect
@dataclass
class ConnectedOrbs(SteppedStatBoost, ExtraBuff):
    # xyzをn個以上つなげて消す
    # triggers if any matched
    orbs: List[Orb] = field(default_factory=list)
    size: int = 0
    size_max: int = 0

    def max_step(self) -> int:
        return self.size_max - self.size

@skill_effect
@dataclass
class ConnectedOrbsAll(BaseStatBoost, ExtraBuff):
    # xyzを"同時"にn個以上つなげて消す
    # triggers if all matched
    orbs: List[Orb] = field(default_factory=list)
    size: int = 0

@skill_effect
@dataclass
class HeartCross(BaseStatBoost, ExtraBuff):
    pass

@skill_effect
@dataclass
class Trigger(BaseStatBoost):
    def calculate_atk(self, combos: List[CCombo], trigger: bool=False,
                      hp: int=100) -> Optional[int]:
        return self.atk if trigger else None

@skill_effect
@dataclass
class EnhancedOrbs5(BaseStatBoost):
    pass

@skill_effect
@dataclass
class MultiplayerGame(BaseStatBoost):
    pass

@skill_effect
@dataclass
class NoSkyfallLS(BaseStatBoost):
    pass

@skill_effect
@dataclass
class MatchFourOrAbove(BaseStatBoost):
    # ドロップをn個以下で消せない
    match: int = 0

@skill_effect
@dataclass
class LShape(BaseStatBoost):
    orbs: List[Orb] = field(default_factory=list)

    def calculate_atk(self, combos: List[CCombo], trigger: bool=False,
                      hp: int=100) -> Optional[int]:
        for c in combos:
            if c.shape == Shape.L and c.orb in self.orbs:
                return self.atk
        return None

@skill_effect
@dataclass
class Board7x6(BaseStatBoost):
    pass

@skill_effect
@dataclass
class OrbRemaining(SteppedStatBoost):
    # パズル後の残りドロップ数がn個以下
    threshold: int = 0

    def max_step(self) -> int:
        return self.threshold if self.atk_step else 1

def leader_skill_177(elements: List[Orb], types: List[Type], hp: int,
                     atk_passive: int, rcv: int, threshold: int, atk: int,
                     atk_step: int) -> MultiEffect:
    # threshold and atk should be both zero or both non-zero
    assert not ((threshold == 0) ^ (atk == 0))

    effect1 = NoSkyfallLS(elements=elements, types=types, hp=hp,
                          atk=atk_passive, rcv=rcv)
    if threshold == 0:
        return MultiEffect(items=[effect1])

    # TODO: figure out if elements/types apply to this as well
    effect2 = OrbRemaining(threshold=threshold, atk=atk, atk_step=atk_step)
    return MultiEffect(items=[effect1, effect2])

@skill_effect
@dataclass
class FixedMovementTime(BaseStatBoost):
    # 操作時間n秒固定
    seconds: int = 0

@skill_effect
@dataclass
class TeamStatBoost(BaseStatBoost):
    card_ids: List[int] = field(default_factory=list)

@skill_effect
@dataclass
class CollaboTeamStatBoost(BaseStatBoost):
    collabo_ids: List[int] = field(default_factory=list)

# xx進化のみでチーム
@skill_effect
@dataclass
class EvoTeamStatBoost(BaseStatBoost):
    # TODO: make a list of this flag
    # known values:
    # 0 - ドット進化
    # 2 - 転生/超転生進化
    evo_flag: int = -1

    def __post_init__(self) -> None:
        super().__post_init__()
        assert self.evo_flag in (0, 2)

@skill_effect
@dataclass
class HealAbove(BaseStatBoost, ExtraBuff):
    threshold: int = 0

# end condition

@skill_effect
@dataclass
class CrossAtkBoost(BaseStatBoost):
    args: InitVar[List[Tuple[Orb, int]]] = field(default=None)
    atk_table: List[int] = field(init=False)

    # pylint: disable=arguments-differ
    def __post_init__(self, args: List[Tuple[Orb, int]] # type: ignore[override]
                      ) -> None:
        super().__post_init__()

        self.atk_table = [0] * 10
        for (o, atk) in args:
            if atk:
                self.atk_table[o] = atk

    def calculate_atk(self, combos: List[CCombo], trigger: bool=False,
                      hp: int=100) -> Optional[int]:
        atk = 100
        for c in combos:
            if c.shape == Shape.CROSS and self.atk_table[c.orb] > 0:
                atk = atk * self.atk_table[c.orb] // 100
        return atk if atk != 100 else None

@skill_effect
@dataclass
class CrossComboIncrease(ExtraBuff):
    orbs: List[Orb] = field(default_factory=list)

def hp_cond_139(elements: List[Orb], types: List[Type], spec: List[List[int]]
                ) -> MultiEffect:
    # tuple[0]: hp condition
    #      [1]: 0=above, 1=below
    #      [2]: atk
    def conv(s: List[int]) -> SkillEffectTag:
        if s[1] == 0:
            return HpAbove(elements=elements, types=types, hp_above=s[0],
                           atk=s[2])
        return HpBelow(elements=elements, types=types, hp_below=s[0], atk=s[2])
    return MultiEffect([conv(s) for s in spec if s[0]])

# pylint: disable=too-many-arguments
def hp_cond_183(elements: List[Orb], types: List[Type],
                hp_above: int, atk_above: int, dr_above: int,
                hp_below: int, atk_below: int, dr_below: int
                ) -> MultiEffect:
    items: List[SkillEffectTag] = []
    if hp_above:
        items.append(HpAbove(elements=elements, types=types, hp_above=hp_above,
                             atk=atk_above, dr=dr_above))
    if hp_below:
        items.append(HpBelow(elements=elements, types=types, hp_below=hp_below,
                             atk=atk_below, dr=dr_below))
    return MultiEffect(items)

DSBParamType = Tuple[List[Orb], List[Type], int, int, int]

def double_stat_boost(params_0: DSBParamType, params_1: DSBParamType
                      ) -> MultiEffect:
    # param = [elements, types, hp, atk, rcv]
    return MultiEffect([
        StatBoost(elements=p[0], types=p[1], hp=p[2], atk=p[3], rcv=p[4])
        for p in [params_0, params_1]
    ])

@skill_effect
@dataclass
class Resolve: # 根性
    hp_threshold: int

@skill_effect
@dataclass
class CounterLS:
    proc_rate: int
    atk: int
    orb: Orb

@skill_effect
@dataclass
class ExtraAttack:
    atk: int

@skill_effect
@dataclass
class ExtraHeal:
    rcv: int

@skill_effect
@dataclass
class TaikoNoise:
    pass

@skill_effect
@dataclass
class Dummy:
    # モンスター経験値アップ, 覚醒スキル解放 etc
    pass

@skill_effect
@dataclass
class RankExpUp:
    percentage: int

@skill_effect
@dataclass
class GoldLootUp:
    percentage: int

@skill_effect
@dataclass
class TreasureLootUp:
    percentage: int

@skill_effect
@dataclass
class PoisonImmune:
    pass

@skill_effect
@dataclass
class SkillSetLS:
    skill_ids: List[int]
