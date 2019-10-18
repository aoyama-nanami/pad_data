#! /usr/bin/env python3

import argparse
import ast
import inspect
import operator

import path_common # pylint: disable=import-error,unused-import

from pad_data import database
from pad_data.leader_skill import effect as ls_effect
from pad_data.active_skill import effect as as_effect
from pad_data.common import Orb


def _atk(card):
    ret = 1
    for e in card.leader_skill.effects:
        if not isinstance(e, ls_effect.BaseStatBoost):
            continue
        if isinstance(e, (ls_effect.HpAbove, ls_effect.HpBelow)):
            continue

        if isinstance(e, ls_effect.SteppedStatBoost) and e.atk_step > 0:
            ret *= (e.atk + e.max_step() * e.atk_step) / 100
        else:
            ret *= e.atk / 100
    return ret

class BaseEvaluator(ast.NodeVisitor):
    def generic_visit(self, node):
        raise Exception(f'Unknown node type: {node}')

    # pylint: disable=invalid-name
    def visit_Expression(self, node):
        return self.visit(node.body)

    # pylint: disable=invalid-name
    def visit_NameConstant(self, node):
        return node.value

    # pylint: disable=invalid-name
    def visit_Num(self, node):
        return node.n

    # pylint: disable=invalid-name
    def visit_Attribute(self, node):
        expr = self.visit(node.value)
        if isinstance(node.ctx, ast.Load):
            if isinstance(expr, dict):
                return expr[node.attr]
            return getattr(expr, node.attr)
        raise NotImplementedError(
            f'Attribute: context {node.ctx} not implemented')

    # pylint: disable=invalid-name
    def visit_BoolOp(self, node):
        op = self._bool_op(node.op)
        return op(self.visit(node.values[0]), self.visit(node.values[1]))

    # pylint: disable=invalid-name
    def visit_Compare(self, node):
        left = self.visit(node.left)
        for op_node, right_node in zip(node.ops, node.comparators):
            right = self.visit(right_node)
            op = self._comp_op(op_node)
            if not op(left, right):
                return False
            left = right
        return True

    # pylint: disable=invalid-name
    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.Not):
            return not self.visit(node.operand)
        raise RuntimeError(f'Unknown operator {node.op}')

    # pylint: disable=invalid-name
    def visit_Call(self, node):
        f = self.visit(node.func)
        return f(*map(self.visit, node.args))

    def _bool_op(self, op):
        if isinstance(op, ast.And):
            return operator.and_
        if isinstance(op, ast.Or):
            return operator.or_
        raise RuntimeError(f'Unknown operator {op}')

    _COMP_OP_MAP = [
        (ast.Eq, operator.eq),
        (ast.NotEq, operator.ne),
        (ast.Lt, operator.lt),
        (ast.LtE, operator.le),
        (ast.Gt, operator.gt),
        (ast.GtE, operator.ge),
        (ast.In, lambda x, y: operator.contains(y, x)),
    ]

    def _comp_op(self, op):
        for cls, func in self._COMP_OP_MAP:
            if isinstance(op, cls):
                return func
        raise RuntimeError(f'Unknown operator {op}')


class SkillEvaluator(BaseEvaluator):
    def __init__(self, cls):
        self._cls = cls
        self._effect = None

    def __call__(self, expr, card):
        effects = (card.skill.effects
                   if self._cls.__module__ == as_effect.__name__
                   else card.leader_skill.effects)
        for e in effects:
            if not isinstance(e, self._cls):
                continue
            self._effect = e
            if self.visit(expr):
                return True
        return False

    # pylint: disable=invalid-name
    def visit_Name(self, node):
        if node.id.isupper():
            return Orb[node.id]
        if node.id == 'len':
            return len
        return getattr(self._effect, node.id)

class RootEvaluator(BaseEvaluator):
    _GLOBALS = {}
    for name, cls in inspect.getmembers(as_effect, inspect.isclass):
        if cls.__module__ != as_effect.__name__:
            continue
        _GLOBALS[name] = SkillEvaluator(cls)
    for name, cls in inspect.getmembers(ls_effect, inspect.isclass):
        if cls.__module__ != ls_effect.__name__:
            continue
        assert name not in _GLOBALS
        _GLOBALS[name] = SkillEvaluator(cls)

    def __init__(self, card):
        self._card = card
        self._locals = {
            'inheritable': lambda: self._card.inheritable,
            'ehp': self._ehp,
            'atk': self._atk,
            'dr': self._dr,
        }

    # pylint: disable=invalid-name
    def visit_Call(self, node):
        f = self.visit(node.func)
        if isinstance(f, SkillEvaluator):
            if node.args:
                return f(node.args[0], self._card)
            return f(ast.NameConstant(value=True), self._card)
        return super().visit_Call(node)

    # pylint: disable=invalid-name
    def visit_Name(self, node):
        value = self._locals.get(node.id)
        if value:
            return value()
        return self._GLOBALS[node.id]

    def _ehp(self):
        ret = 1
        for e in self._card.leader_skill.effects:
            if not isinstance(e, ls_effect.BaseStatBoost):
                continue
            if isinstance(e, (ls_effect.HpAbove, ls_effect.HpBelow)):
                continue
            ret *= e.effective_hp()
        return ret

    def _atk(self):
        return _atk(self._card)

    def _dr(self):
        ret = 1
        for e in self._card.leader_skill.effects:
            if not isinstance(e, ls_effect.BaseStatBoost):
                continue
            if isinstance(e, (ls_effect.HpAbove, ls_effect.HpBelow)):
                continue
            ret *= (1 - e.dr / 100)
        return (1 - ret) * 100


HELP = f'''
examples of filter expression:

    %(prog)s '(RowChange() or ColumnChange()) and Nuke()'
    filter by skill type

    %(prog)s 'RandomOrbSpawn(count >= 10 and FIRE in orb)'
    filter by skill type and sub contraint

    %(prog)s 'dr >= 40 and atk >= 16'
    special keywords: inheritable, atk, dr, and ehp
'''

def main():
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

    cards = filter(lambda c: RootEvaluator(c).visit(tree), cards)
    if args.print_leader_skill:
        cards = sorted(cards, key=_atk)
    else:
        cards = sorted(cards, key=lambda c: c.skill.turn_min)
    for c in cards:
        c.dump(print_leader_skill=args.print_leader_skill,
               print_active_skill=not args.print_leader_skill)

if __name__ == '__main__':
    main()
