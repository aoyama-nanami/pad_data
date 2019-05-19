import functools
import json

from pad_data import card, common, active_skill, skill

RESISTS = [common.EnemySkill.VOID_SHIELD,
           common.EnemySkill.ELEMENT_RESIST,
           common.EnemySkill.TYPE_RESIST]

class Database:
    def __init__(self, raw_cards_json='data/processed/jp_raw_cards.json',
                 skills_json='data/processed/jp_skills.json',
                 enemy_skills_json='data/processed/jp_enemy_skills.json'):
        with open(raw_cards_json, 'r') as f:
            self._cards = dict(
                (c['card_id'], card.Card(c)) for c in json.load(f))

        with open(skills_json, 'r') as f:
            self._skills = dict((s['skill_id'], s) for s in json.load(f))

        with open(enemy_skills_json, 'r') as f:
            enemy_skills = dict((s['enemy_skill_id'], s) for s in json.load(f))

        for c in self._cards.values():
            raw_effects = self._expand_skill(c.active_skill_id)
            if c.active_skill_id == 0:
                c.skill = card.Skill('', '', '', [], 0, 0, raw_effects)
                continue
            s = self._skills[c.active_skill_id]
            name = s['name']
            clean_description = s['clean_description']
            description = s['description']
            turn_max = s['turn_max']
            turn_min = s['turn_min']
            effects = []
            for s in raw_effects:
                try:
                    e = skill.parse(s['skill_type'], s['other_fields'])
                    effects.append(e)
                except Exception:
                    print(c.card_id, description, s, sep=' ')
                    raise
            active_skill.post_process(effects)
            c.skill = card.Skill(
                name, clean_description, description, effects, turn_max,
                turn_min, raw_effects)

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

    def _expand_skill(self, skill_id):
        s = self._skills[skill_id]

        if s['skill_type'] != skill.ACTIVE_SKILL_SET:
            return [s]

        return functools.reduce(list.__iadd__,
                                map(self._expand_skill, s['other_fields']),
                                [])

    def get_all_released_cards(self):
        return list(filter(
            lambda c: c.card_id <= 10000 and c.released_status,
            self._cards.values()))
