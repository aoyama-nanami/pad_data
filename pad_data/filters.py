from . import common

class Filter:
    pass

class SkillFilterBase(Filter):
    def __init__(self, cls, expr):
        super().__init__()
        self._cls = cls
        self._expr = expr

    def _effect_match(self, effect):
        if not isinstance(effect, self._cls):
            return False
        # pylint: disable=eval-used
        return eval(self._expr, self._GLOBALS, {'_': effect})

    def _get_effects(self, card):
        raise NotImplementedError

    def __call__(self, card):
        return any(self._effect_match(e) for e in self._get_effects(card))

    _GLOBALS = dict(**common.Awakening.__members__,
                    **common.Orb.__members__,
                    **common.Type.__members__)

class Skill(SkillFilterBase):
    def _get_effects(self, card):
        return card.skill.effects

class LeaderSkill(SkillFilterBase):
    def _get_effects(self, card):
        return card.leader_skill.effects
