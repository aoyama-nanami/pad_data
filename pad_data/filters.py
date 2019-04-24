class Filter:
    pass

class Skill(Filter):
    def __init__(self, cls, f):
        self._cls = cls
        self._f = f

    def _effect_match(self, effect):
        if not isinstance(effect, self._cls):
            return False
        return self._f.apply(effect)

    def __call__(self, card):
        return any(self._effect_match(e) for e in card.skill.effects)

class Placeholder:
    def __init__(self, f=lambda x: x):
        self.apply = f

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(f'access to {name} not allowed')
        return Placeholder(lambda x: getattr(self.apply(x), name))

    @staticmethod
    def _maybe_apply(placeholder, x):
        return (placeholder.apply(x) if isinstance(placeholder, Placeholder)
                else x)

    # bitwise and
    # override of binary and/or/not not allowed
    def __and__(self, other):
        return Placeholder(
            lambda x: self.apply(x) and self._maybe_apply(other, x))

    # bitwise or
    def __or__(self, other):
        return Placeholder(
            lambda x: self.apply(x) or self._maybe_apply(other, x))

    # bitwise not
    def __not__(self):
        return Placeholder(lambda x: not self.apply(x))

    @classmethod
    def gen_proxy(cls, funcname):
        def proxy(self, *args):
            return cls(lambda x: getattr(self.apply(x), funcname)(*args))
        setattr(cls, funcname, proxy)

Placeholder.gen_proxy('__lt__')
Placeholder.gen_proxy('__le__')
Placeholder.gen_proxy('__eq__')
Placeholder.gen_proxy('__ne__')
Placeholder.gen_proxy('__gt__')
Placeholder.gen_proxy('__ge__')

Placeholder.gen_proxy('__call__')
Placeholder.gen_proxy('__getitem__')
Placeholder.gen_proxy('__contains__')
Placeholder.gen_proxy('__len__')
