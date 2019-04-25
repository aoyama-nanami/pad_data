from . import common

class Filter:
    pass

class Skill(Filter):
    def __init__(self, cls, expr):
        self._cls = cls
        self._expr = expr

    def _effect_match(self, effect):
        if not isinstance(effect, self._cls):
            return False
        # pylint: disable=eval-used
        return eval(self._expr, self._GLOBALS, {'_': effect})

    def __call__(self, card):
        return any(self._effect_match(e) for e in card.skill.effects)

    _GLOBALS = dict(**common.Awakening.__members__,
                    **common.Orb.__members__,
                    **common.Type.__members__)
