import functools
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

class Database:
    def __init__(self, raw_cards_json='data/processed/jp_raw_cards.json',
                 skills_json='data/processed/jp_skills.json',
                 enemy_skills_json='data/processed/jp_enemy_skills.json'):
        project_root = os.path.join(os.path.dirname(__file__), '..')

        with open(os.path.join(project_root, raw_cards_json), 'r') as f:
            self._cards = dict(
                (c['card_id'], card.Card(c)) for c in json.load(f))

        with open(os.path.join(project_root, skills_json), 'r') as f:
            self._skills = dict((s['skill_id'], s) for s in json.load(f))

        with open(os.path.join(project_root, enemy_skills_json), 'r') as f:
            enemy_skills = dict((s['enemy_skill_id'], s) for s in json.load(f))

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
                s = enemy_skills[ref['enemy_skill_id']]
                skills.append(s)
                if s['type'] == common.EnemySkill.SKILL_SET:
                    for skill_id in filter(lambda x: x, s['params'][1:]):
                        skills.append(enemy_skills[skill_id])

            for s in filter(lambda s: s['type'] in RESISTS, skills):
                skill_id = s['enemy_skill_id']
                combined_skill_data = card.EnemyPassiveResist(
                    skill_id,
                    c.name,
                    s['type'],
                    s['name'],
                    s['params'][1:],
                )
                self._cards[card_id].enemy_passive_resist[skill_id] = \
                        combined_skill_data

    def card(self, card_id):
        return self._cards[card_id]

    def _process_skill(self, skill_id, is_active_skill):
        if skill_id == 0:
            return card.Skill('', '', '', [], 0, 0, [])
        raw_effects = self._expand_skill(skill_id)
        s = self._skills[skill_id]
        name = s['name']
        clean_description = s['clean_description']
        description = s['description']
        turn_max = s['turn_max']
        turn_min = s['turn_min']
        effects = []
        for s in raw_effects:
            try:
                e = skill.parse(s['skill_type'], s['other_fields'],
                                is_active_skill)
                effects.append(e)
            except Exception:
                raise UnknownSkillEffect(clean_description, raw_effects)
        if is_active_skill:
            active_skill.post_process(effects)
        else:
            effects = leader_skill.post_process(effects)
        return card.Skill(
            name, clean_description, description, effects, turn_max,
            turn_min, raw_effects)

    def _expand_skill(self, skill_id):
        s = self._skills[skill_id]

        if s['skill_type'] not in SKILL_SET_ID:
            return [s]

        return functools.reduce(list.__iadd__,
                                map(self._expand_skill, s['other_fields']),
                                [])

    def get_all_released_cards(self):
        return list(filter(
            lambda c: c.card_id <= 10000 and c.released_status,
            self._cards.values()))
