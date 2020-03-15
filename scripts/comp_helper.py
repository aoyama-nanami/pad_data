#! /usr/bin/env python3

import dataclasses
from inspect import getmembers, getmodule, isclass
import re
import sys
from types import ModuleType
from typing import List, Tuple

import path_common # pylint: disable=import-error,unused-import

from pad_data.active_skill import effect as as_effect
from pad_data.leader_skill import effect as ls_effect
from pad_data.skill import SkillEffectTag


def get_skill_effects_from_module(module: ModuleType) -> List[Tuple[str, type]]:
    return getmembers(module, lambda x: (isclass(x) and getmodule(x) == module
                                         and issubclass(x, SkillEffectTag)))

def main() -> None:
    if len(sys.argv) != 2:
        return

    prefix = sys.argv[1]
    tokens = re.findall(r'([A-Za-z0-9_]+|\(|\))', prefix)

    skill_effects = {}
    for name, cls in get_skill_effects_from_module(as_effect):
        skill_effects[name] = cls
    for name, cls in get_skill_effects_from_module(ls_effect):
        assert name not in skill_effects
        skill_effects[name] = cls

    stack = [None]
    try:
        for token in tokens:
            if token == '(':
                stack.append(None)
            elif token == ')':
                stack.pop()
            else:
                stack[-1] = token
    except IndexError:
        # brace not matched?, ignore
        return

    for token in stack[::-1]:
        if token not in skill_effects:
            continue
        print(*(f.name for f in dataclasses.fields(skill_effects[token])),
              sep=' ')
        return

    print(*skill_effects.keys(), sep=' ')


if __name__ == '__main__':
    main()
