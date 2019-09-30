from . import common

class Filter:
    @property
    def is_active_skill(self):
        raise NotImplementedError

    def __call__(self, card):
        raise NotImplementedError

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

class Skill(Filter):
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
        if self.is_active_skill:
            return card.skill.effects
        return card.leader_skill.effects

    def __call__(self, card):
        return any(self._effect_match(e) for e in self._get_effects(card))

    @property
    def is_active_skill(self):
        return self._cls.__module__ == 'pad_data.active_skill.effect'

    _GLOBALS = dict(**common.Awakening.__members__,
                    **common.Orb.__members__,
                    **common.Type.__members__)

class Inheritable(Filter):
    def __call__(self, card):
        return card.inheritable

    @property
    def is_active_skill(self):
        return True

INHERITABLE = Inheritable()

class And(Filter):
    def __init__(self, x, y):
        super().__init__()
        self._lhs = x
        self._rhs = y

    def __call__(self, card):
        return self._lhs(card) and self._rhs(card)

    @property
    def is_active_skill(self):
        return self._lhs.is_active_skill and self._rhs.is_active_skill

class Or(Filter):
    def __init__(self, x, y):
        super().__init__()
        self._lhs = x
        self._rhs = y

    def __call__(self, card):
        return self._lhs(card) or self._rhs(card)

    @property
    def is_active_skill(self):
        return self._lhs.is_active_skill and self._rhs.is_active_skill
