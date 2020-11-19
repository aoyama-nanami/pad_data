import json
import os.path
import traceback
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from typing import TextIO, Tuple

from pad_data import active_skill, enemy_skill, leader_skill
from pad_data.card import Card
from pad_data.skill import Skill, SkillEffectTag, skill_parser

def parse_csv(raw: str) -> Iterable[List[str]]:
    i = 0
    line = []
    while i < len(raw):
        if raw[i] == "'":
            end = i
            while True:
                end = raw.find("'", end + 1)
                assert end >= 0, 'cannot find matching quotes'
                if (end + 1 == len(raw) or raw[end + 1] == ',' or
                        raw[end + 1] == '\n'):
                    break
            line.append(raw[i + 1 : end])
            if end + 1 == len(raw) or raw[end + 1] == '\n':
                yield line
                line = []
            i = end + 2
        else:
            s = ''
            while i < len(raw) and raw[i] != ',' and raw[i] != '\n':
                s += raw[i]
                i += 1
            line.append(s)
            if i == len(raw) or raw[i] == '\n':
                yield line
                line = []
            i += 1

def skill_debug(skills: Mapping[int, Skill], skill_id: int, name: str,
                description: str, skill_type: int, params: List[int],
                extra_items: Mapping[str, Any]) -> None:
    # find the skill set containing this skill_id:
    for s in skills.values():
        if not s.effects:
            continue
        if isinstance(s.effects[0],
                      (active_skill.effect.SkillSet,
                       leader_skill.effect.SkillSetLS)):
            if skill_id in s.effects[0].skill_ids:
                name = s.name
                description = s.description
                break
    print(f'Failed:')
    print(f'{skill_id=} {name=} {description=}')
    print(f'{skill_type=}')
    print(f'{params=}')
    if extra_items:
        print(f'{extra_items=}')
    print('=' * 30)

class Database:
    def __init__(self, card_json: str='data/raw/download_card_data.json',
                 skill_json: str='data/raw/download_skill_data.json',
                 enemy_skill_json: str='data/raw/download_enemy_skill_data.json'
                 ) -> None:
        project_root = os.path.join(os.path.dirname(__file__), '..')

        with open(os.path.join(project_root, card_json), 'r') as f:
            self._cards = self._parse_card_json(f)

        with open(os.path.join(project_root, skill_json), 'r') as f:
            self._raw_skills: MutableMapping[int, Tuple[int, List[int]]] = {}
            self._skills = self._parse_skill_json(f)

        with open(os.path.join(project_root, enemy_skill_json), 'r') as f:
            enemy_skills = self._parse_enemy_skill_json(f)

        for c in self._cards.values():
            if c.card_id >= 100000:
                continue
            c.skill = self._process_skill(c.active_skill_id, True)
            c.leader_skill = self._process_skill(c.leader_skill_id, False)

        for c in self._cards.values():
            card_id = c.card_id % 100000
            passives = {}
            for ref in c.enemy_skill_refs:
                if ref.enemy_skill_id not in enemy_skills:
                    continue
                s = enemy_skills[ref.enemy_skill_id]
                if isinstance(s.effects[0], enemy_skill.effect.SkillSetES):
                    for sub_skill_id in s.effects[0].skill_ids:
                        if sub_skill_id in enemy_skills:
                            passives[sub_skill_id] = enemy_skills[sub_skill_id]
                else:
                    passives[ref.enemy_skill_id] = s

            if card_id in self._cards:
                self._cards[card_id].enemy_passive_resist.update(passives)

    def card(self, card_id: int) -> Card:
        return self._cards[card_id]

    @staticmethod
    def _check_file_version(name: str, new: int, old: int) -> None:
        if new != old:
            print(f'\x1b[1;33mWARNING: {name} version changed: ' +
                  f'{old} -> {new}\x1b[m')

    def _parse_card_json(self, f: TextIO) -> Mapping[int, Card]:
        obj = json.load(f)
        # version downgraded from 1800 to 1600 in ver 18.60?
        self._check_file_version('card json', obj['v'], 1600)
        return dict((c[0], Card(c)) for c in obj['card'])

    KNOWN_BAD_SKILLS = frozenset([
        494,   # type=2, params=[1, 50, 50000]
        2317,  # type=89, params=[100]
        8260,  # type=14, params=[]
        10178, # type=140, params=[]
        13267, # type=151, params=[0, 300, 50]
        17336, # type=156, params=[2, 100, 0, 0, 0, 0, 63]
    ])

    def _parse_skill_json(self, f: TextIO) -> Mapping[int, Skill]:
        obj = json.load(f)
        skills: MutableMapping[int, Skill] = {}
        failed = False
        for i, raw in enumerate(obj['skill']):
            if i in self.KNOWN_BAD_SKILLS:
                continue
            name = raw.pop('name')
            description = raw.pop('help')
            skill_type = raw.pop('sktp')
            levels = raw.pop('lcap')
            turn_max = raw.pop('ctbs')
            turn_min = turn_max - levels + 1
            params = [raw.pop(f'skp{x}', 0) for x in range(1, 10)]
            while params and params[-1] == 0:
                params.pop()
            self._raw_skills[i] = (skill_type, params)
            try:
                assert raw.pop('ctel') in (0, -1)
                assert not raw # assert no unknown keys
                effect = [skill_parser.parse(skill_type, params)]
            except (RuntimeError, KeyError, AssertionError, ValueError):
                traceback.print_exc()
                skill_debug(skills, i, name, description, skill_type, params,
                            raw)
                failed = True
            else:
                skills[i] = Skill(name, description, effect, turn_max, turn_min)
        skills[0] = Skill('', '', [], 0, 0)
        if failed:
            raise Exception('parse_skill_json failed')
        return skills

    def _parse_enemy_skill_json(self, f: TextIO) -> Mapping[int, Skill]:
        obj = json.load(f)
        self._check_file_version('skill json', obj['v'], 2)
        enemy_skills = {}
        for raw in parse_csv(obj['enemy_skills']):
            if raw[0] == 'c':
                continue
            try:
                skill_id = int(raw[0])
                name = raw[1]
                skill_type = int(raw[2])
                flags = int(raw[3], 16)
                params = [0] * 15
                offset = 0
                p_idx = 4
                description = ''
                while flags > 0:
                    if flags & 1:
                        p_value = raw[p_idx]
                        if offset == 0:
                            description = p_value
                        else:
                            params[offset - 1] = int(p_value)
                        p_idx += 1
                    offset += 1
                    flags >>= 1
                try:
                    e = skill_parser.parse_enemy_skill(skill_type, params)
                    enemy_skills[skill_id] = Skill(name, description, [e], 0, 0)
                except KeyError:
                    # ignore unhandled skill types
                    pass
                except Exception:
                    print(f'Parse enemy skill failed:')
                    print(f'{name=} {description=}')
                    print(f'{skill_type=}')
                    print(f'{params=}')
                    raise
            except Exception:
                print('failed to parse enemy skill csv, error at:')
                print(raw)
                raise
        return enemy_skills

    def _process_skill(self, skill_id: int, is_active_skill: bool) -> Skill:
        effects = self._expand_skill(skill_id)
        s = self._skills[skill_id]
        if is_active_skill:
            active_skill.post_process(effects)
            assert all(e.__module__ == 'pad_data.active_skill.effect'
                       for e in effects)
        else:
            effects = leader_skill.post_process(effects)
            assert all(e.__module__ == 'pad_data.leader_skill.effect'
                       for e in effects)
        return Skill(s.name, s.description, effects, s.turn_max, s.turn_min)

    def _expand_skill(self, skill_id: int) -> List[SkillEffectTag]:
        expanded: List[SkillEffectTag] = []
        s = self._skills[skill_id]

        for e in s.effects:
            if isinstance(e, (active_skill.effect.SkillSet,
                              leader_skill.effect.SkillSetLS)):
                for x in e.skill_ids:
                    expanded += self._expand_skill(x)
            else:
                expanded.append(e)
        return expanded

    def get_all_released_cards(self) -> List[Card]:
        return list(filter(
            lambda c: c.card_id <= 10000 and c.released_status,
            self._cards.values()))

    def print_raw_skills(self, skill_id: int) -> None:
        skill_type, params = self._raw_skills[skill_id]
        print(skill_type, params)

        if skill_type in (skill_parser.ACTIVE_SKILL_SET,
                          skill_parser.LEADER_SKILL_SET):
            for x in params:
                self.print_raw_skills(x)
