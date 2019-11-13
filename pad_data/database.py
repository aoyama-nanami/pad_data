import json
import os.path

from pad_data import active_skill, card, common, leader_skill, skill

RESISTS = [common.EnemySkill.VOID_SHIELD,
           common.EnemySkill.ELEMENT_RESIST,
           common.EnemySkill.TYPE_RESIST]

SKILL_SET_ID = [skill.ACTIVE_SKILL_SET, skill.LEADER_SKILL_SET]

class UnknownSkillEffect(Exception):
    def __init__(self, desc, effects):
        super().__init__()
        self.desc = desc
        self.effects = effects

def parse_csv(raw):
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

class Database:
    def __init__(self, card_json='data/raw/jp/download_card_data.json',
                 skill_json='data/raw/jp/download_skill_data.json',
                 enemy_skill_json='data/raw/jp/download_enemy_skill_data.json'
                 ):
        project_root = os.path.join(os.path.dirname(__file__), '..')

        with open(os.path.join(project_root, card_json), 'r') as f:
            self._cards = self._parse_card_json(f)

        with open(os.path.join(project_root, skill_json), 'r') as f:
            self._skills = self._parse_skill_json(f)

        with open(os.path.join(project_root, enemy_skill_json), 'r') as f:
            enemy_skills = self._parse_enemy_skill_json(f)

        for c in self._cards.values():
            try:
                c.skill = self._process_skill(c.active_skill_id, True)
                c.leader_skill = self._process_skill(c.leader_skill_id, False)
            except UnknownSkillEffect as e:
                print(c.card_id, c.name)
                print(e.desc)
                print(e.effects)
                raise

        for c in self._cards.values():
            card_id = c.card_id % 100000
            skills = []
            for ref in c.enemy_skill_refs:
                s = enemy_skills[ref.enemy_skill_id]
                skills.append(s)
                if s['type'] == common.EnemySkill.SKILL_SET:
                    for skill_id in filter(bool, s['params']):
                        skills.append(enemy_skills[skill_id])

            for s in filter(lambda s: s['type'] in RESISTS, skills):
                skill_id = s['skill_id']
                combined_skill_data = card.EnemyPassiveResist(
                    skill_id,
                    c.name,
                    s['type'],
                    s['name'],
                    s['params'],
                )
                self._cards[card_id].enemy_passive_resist[skill_id] = \
                        combined_skill_data

    def card(self, card_id):
        return self._cards[card_id]

    def _check_file_version(self, name, new, old):
        if new != old:
            print(f'\x1b[1;33mWARNING: {name} version changed: ' +
                  f'{old} -> {new}\x1b[m')

    def _parse_card_json(self, f):
        obj = json.load(f)
        self._check_file_version('card json', obj['v'], 1800)
        return dict((c[0], card.Card(c)) for c in obj['card'])

    KNOWN_BAD_SKILLS = frozenset([
        494,   # type=2, params=[1, 50, 50000]
        2317,  # type=89, params=[100]
        8260,  # type=14, params=[]
        8333,  # type=156, params=[]
        8334,  # type=156, params=[]
        8394,  # type=156, params=[]
        8395,  # type=156, params=[]
        10178, # type=140, params=[]
        13267, # type=151, params=[0, 300, 50]
    ])

    def _parse_skill_json(self, f):
        obj = json.load(f)
        self._check_file_version('skill json', obj['v'], 1220)
        skills = {}
        for i, raw in enumerate(obj['skill']):
            if i in self.KNOWN_BAD_SKILLS:
                continue
            s = {}
            name = raw[0]
            description = raw[1]
            skill_type = int(raw[2])
            levels = int(raw[3])
            turn_max = int(raw[4]) if levels else None
            turn_min = (turn_max - levels + 1 if levels else None)
            params = list(map(int, raw[6:]))
            try:
                effect = [skill.parse(skill_type, params)]
            except Exception:
                print(s)
                raise
            skills[i] = card.Skill(name, description, effect, turn_max,
                                   turn_min)
        skills[0] = card.Skill('', '', [], 0, 0)
        return skills

    def _parse_enemy_skill_json(self, f):
        obj = json.load(f)
        self._check_file_version('skill json', obj['v'], 2)
        enemy_skills = {}
        for raw in parse_csv(obj['enemy_skills']):
            if raw[0] == 'c':
                continue
            s = {}
            try:
                s['skill_id'] = int(raw[0])
                s['name'] = raw[1]
                s['type'] = int(raw[2])
                flags = int(raw[3], 16)
                params = [None] * 16
                offset = 0
                p_idx = 4
                while flags > 0:
                    if flags & 1:
                        p_value = raw[p_idx]
                        try:
                            params[offset] = int(p_value)
                        except ValueError:
                            params[offset] = p_value
                        p_idx += 1
                    offset += 1
                    flags >>= 1
                s['description'] = params[0]
                s['params'] = params[1:]
                enemy_skills[s['skill_id']] = s
            except Exception:
                print('failed to parse enemy skill csv, error at:')
                print(raw)
                raise
        return enemy_skills

    def _process_skill(self, skill_id, is_active_skill):
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
        return card.Skill(
            s.name, s.description, effects, s.turn_max, s.turn_min)

    def _expand_skill(self, skill_id):
        expanded = []
        s = self._skills[skill_id]

        for e in s.effects:
            if isinstance(e, (active_skill.effect.SkillSet,
                              leader_skill.effect.SkillSetLS)):
                for x in e.skill_ids:
                    expanded += self._expand_skill(x)
            else:
                expanded.append(e)
        return expanded

    def get_all_released_cards(self):
        return list(filter(
            lambda c: c.card_id <= 10000 and c.released_status,
            self._cards.values()))
