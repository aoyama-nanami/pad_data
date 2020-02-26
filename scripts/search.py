#! /usr/bin/env python3

import argparse
import ast
from contextlib import contextmanager
from dataclasses import asdict
import inspect
import operator
from typing import Any, Iterator, Mapping, NoReturn, Type

import path_common # pylint: disable=import-error,unused-import

from pad_data import database
from pad_data.active_skill import effect as as_effect
from pad_data.card import Card
from pad_data.common import Orb
from pad_data.leader_skill import effect as ls_effect
from pad_data.skill import SkillEffectTag
from pad_data.util.lazy_dict import LazyDict


def _atk(card: Card) -> int:
    ret: float = 1
    for e in card.leader_skill.effects:
        if not isinstance(e, ls_effect.BaseStatBoost):
            continue
        if isinstance(e, (ls_effect.HpAbove, ls_effect.HpBelow)):
            continue
        # some skill type does not fill in atk field
        if e.atk == 0:
            continue

        if isinstance(e, ls_effect.SteppedStatBoost) and e.atk_step > 0:
            ret *= (e.atk + e.max_step() * e.atk_step) / 100
        else:
            ret *= e.atk / 100
    return int(ret)

class BaseEvaluator(ast.NodeVisitor):
    _BUILTINS: Mapping[str, Any] = {
         'len': len,
         'sum': sum,
         'min': min,
         'max': max,
         'set': set,
    }

    def __init__(self, *namespaces: Mapping[str, Any]):
        self.namespaces = [self._BUILTINS] + list(namespaces)

    @contextmanager
    def _push_namespace(self, namespace: Mapping[str, Any]) -> Iterator[None]:
        try:
            self.namespaces.append(namespace)
            yield
        finally:
            self.namespaces.pop()

    def generic_visit(self, node: Any) -> NoReturn:
        raise Exception(f'Unknown node type: {node}')

    # pylint: disable=invalid-name
    def visit_Name(self, node: ast.Name) -> Any:
        key = node.id

        for namespace in self.namespaces[::-1]:
            if key in namespace:
                return namespace[key]
        raise KeyError(key)

    # pylint: disable=invalid-name
    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    # pylint: disable=invalid-name,no-self-use
    def visit_NameConstant(self, node: ast.NameConstant) -> Any:
        return node.value

    # pylint: disable=invalid-name,no-self-use
    def visit_Num(self, node: ast.Num) -> Any:
        return node.n

    # pylint: disable=invalid-name
    def visit_Attribute(self, node: ast.Attribute) -> Any:
        expr = self.visit(node.value)
        if isinstance(node.ctx, ast.Load):
            if isinstance(expr, dict):
                return expr[node.attr]
            return getattr(expr, node.attr)
        raise NotImplementedError(
            f'Attribute: context {node.ctx} not implemented')

    # pylint: disable=invalid-name
    def visit_BoolOp(self, node: ast.BoolOp) -> bool:
        if isinstance(node.op, ast.And):
            for x in node.values:
                if not self.visit(x):
                    return False
            return True

        # ast.Or
        for x in node.values:
            if self.visit(x):
                return True
        return False

    # pylint: disable=invalid-name
    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)

        for cls, func in self._BIN_OP_MAP:
            if isinstance(node.op, cls):
                return func(left, right)
        raise RuntimeError(f'Unknown operator {node.op}')

    # pylint: disable=invalid-name
    def visit_Compare(self, node: ast.Compare) -> Any:
        left = self.visit(node.left)
        for op_node, right_node in zip(node.ops, node.comparators):
            right = self.visit(right_node)
            op = self._comp_op(op_node)
            if not op(left, right):
                return False
            left = right
        return True

    # pylint: disable=invalid-name
    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        if isinstance(node.op, ast.Not):
            return not self.visit(node.operand)
        raise RuntimeError(f'Unknown operator {node.op}')

    # pylint: disable=invalid-name
    def visit_Call(self, node: ast.Call) -> Any:
        f = self.visit(node.func)
        # TODO: implement kwargs?
        return f(*map(self.visit, node.args))

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        v = self.visit(node.value)
        i = self.visit(node.slice)
        return v[i]

    def visit_Index(self, node: ast.Index) -> Any:
        return self.visit(node.value)

    def visit_List(self, node: ast.List) -> Any:
        return [self.visit(x) for x in node.elts]

    def visit_Set(self, node: ast.Set) -> Any:
        return {self.visit(x) for x in node.elts}

    def visit_ListComp(self, node: ast.ListComp) -> Any:
        assert len(node.generators) == 1

        res = []
        generator = node.generators[0]
        # no tuple unpacking support for now
        assert isinstance(generator.target, ast.Name)
        name = generator.target.id

        for v in self.visit(generator.iter):
            with self._push_namespace({name: v}):
                if all(self.visit(x) for x in generator.ifs):
                    res.append(self.visit(node.elt))
        return res

    _COMP_OP_MAP = [
        (ast.Eq, operator.eq),
        (ast.NotEq, operator.ne),
        (ast.Lt, operator.lt),
        (ast.LtE, operator.le),
        (ast.Gt, operator.gt),
        (ast.GtE, operator.ge),
        (ast.In, lambda x, y: operator.contains(y, x)),
    ]

    def _comp_op(self, op: Any) -> Any:
        for cls, func in self._COMP_OP_MAP:
            if isinstance(op, cls):
                return func
        raise RuntimeError(f'Unknown operator {op}')

    _BIN_OP_MAP = [
        (ast.Add, operator.add),
        (ast.Sub, operator.sub),
        (ast.Mult, operator.mul),
        (ast.MatMult, operator.matmul),
        (ast.Div, operator.truediv),
        (ast.Mod, operator.mod),
        (ast.Pow, operator.pow),
        (ast.LShift, operator.lshift),
        (ast.RShift, operator.rshift),
        (ast.BitOr, operator.or_),
        (ast.BitXor, operator.xor),
        (ast.BitAnd, operator.and_),
        (ast.FloorDiv, operator.floordiv),
    ]


class SkillEvaluator(BaseEvaluator):
    def __init__(self, cls: Type[SkillEffectTag]):
        super().__init__(Orb.__members__)
        self._cls = cls

    def __call__(self, expr: ast.AST, card: Card) -> bool:
        effects = (card.skill.effects
                   if self._cls.__module__ == as_effect.__name__
                   else card.leader_skill.effects)
        for effect in effects:
            if not isinstance(effect, self._cls):
                continue
            with self._push_namespace(asdict(effect)):
                if self.visit(expr):
                    return True
        return False

class RootEvaluator(BaseEvaluator):
    _SKILL_EFFECTS = {}
    for name, cls in inspect.getmembers(as_effect, inspect.isclass):
        if cls.__module__ != as_effect.__name__:
            continue
        _SKILL_EFFECTS[name] = SkillEvaluator(cls)
    for name, cls in inspect.getmembers(ls_effect, inspect.isclass):
        if cls.__module__ != ls_effect.__name__:
            continue
        assert name not in _SKILL_EFFECTS
        _SKILL_EFFECTS[name] = SkillEvaluator(cls)

    def __init__(self, card: Card):
        super().__init__(
                self._SKILL_EFFECTS,
                LazyDict({
                    'inheritable': card.inheritable,
                    'rarity': card.rarity,
                    'ehp': self._ehp,
                    'atk': self._atk,
                    'dr': self._dr,
                    'cd': self._cd,
                }))
        self._card = card

    # pylint: disable=invalid-name
    def visit_Call(self, node: ast.Call) -> Any:
        f = self.visit(node.func)
        if isinstance(f, SkillEvaluator):
            if node.args:
                return f(node.args[0], self._card)
            return f(ast.NameConstant(value=True), self._card)
        return super().visit_Call(node)

    def _ehp(self) -> float:
        ret: float = 1
        for e in self._card.leader_skill.effects:
            if not isinstance(e, ls_effect.BaseStatBoost):
                continue
            if isinstance(e, (ls_effect.HpAbove, ls_effect.HpBelow)):
                continue
            ret *= e.effective_hp()
        return ret

    def _atk(self) -> float:
        return _atk(self._card)

    def _dr(self) -> float:
        ret: float = 1
        for e in self._card.leader_skill.effects:
            if not isinstance(e, ls_effect.BaseStatBoost):
                continue
            if isinstance(e, (ls_effect.HpAbove, ls_effect.HpBelow)):
                continue
            ret *= (1 - e.dr / 100)
        return (1 - ret) * 100

    def _cd(self) -> int:
        if self._card.skill.turn_min is not None:
            return self._card.skill.turn_min
        raise TypeError


HELP = f'''
examples of filter expression:

    %(prog)s '(RowChange() or ColumnChange()) and Nuke()'
    filter by skill type

    %(prog)s 'RandomOrbSpawn(count >= 10 and FIRE in orb)'
    filter by skill type and sub contraint

    %(prog)s 'dr >= 40 and atk >= 16'
    special keywords: inheritable, atk, dr, and ehp
'''

def main() -> None:
    parser = argparse.ArgumentParser(
        epilog=HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('expr', metavar='EXPR', type=str, nargs=1,
                        help='filter expression')
    parser.add_argument('-l', action='store_true', dest='print_leader_skill',
                        help='print leader skill')
    args = parser.parse_args()

    db = database.Database()
    cards = db.get_all_released_cards()
    tree = ast.parse(args.expr[0].replace('\n', ' ').strip(), mode='eval')

    cards = list(filter(lambda c: RootEvaluator(c).visit(tree), cards))
    if args.print_leader_skill:
        cards = sorted(cards, key=_atk)
    else:
        cards = sorted(cards, key=lambda c: c.skill.turn_min)
    for c in cards:
        c.dump(print_leader_skill=args.print_leader_skill,
               print_active_skill=not args.print_leader_skill)

if __name__ == '__main__':
    main()
