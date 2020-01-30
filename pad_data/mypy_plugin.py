from typing import cast, Callable, Optional

from mypy.nodes import SymbolTableNode, TypeInfo
from mypy.plugin import ClassDefContext, Plugin
from mypy.types import Instance

Hook = Optional[Callable[[ClassDefContext], None]]

class PatchBaseClass:
    def __init__(self, classname: str):
        self.classname = classname

    def __call__(self, context: ClassDefContext) -> None:
        info = context.cls.info
        api = context.api

        if (tag := api.lookup_fully_qualified_or_none(self.classname)) is None:
            api.fail(f'{self.classname} not found', context.cls)
            return

        # mypy can't recognize the `is None` check above.
        tag = cast(SymbolTableNode, tag)

        if not isinstance(tag.node, TypeInfo):
            api.fail(f'{self.classname} is not a class', context.cls)
            return

        if tag.node not in info.mro:
            info.mro[-1:-1] = [tag.node]
        # seems redundant? add this only for consistency
        info.bases[-1:-1] = [Instance(tag.node, [])]

class PADDataPlugin(Plugin):
    @staticmethod
    def get_class_decorator_hook(fullname: str) -> Hook:
        if fullname == 'pad_data.skill.skill_effect':
            return PatchBaseClass('pad_data.skill.base.SkillEffectTag')
        return None

# pylint: disable=unused-argument
def plugin(version: str) -> type:
    return PADDataPlugin
