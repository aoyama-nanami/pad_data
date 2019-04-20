import functools
import json
from .common import Card, Skill
from .skill_type import parse_skill_effect, MULTI_EFFECT_ID

class Database:
    def __init__(self, raw_cards_json='data/processed/jp_raw_cards.json',
                 skills_json='data/processed/jp_skills.json'):
        with open(raw_cards_json, 'r') as f:
            self._cards = dict((c['card_id'], Card(c)) for c in json.load(f))

        with open(skills_json, 'r') as f:
            self._skills = dict((s['skill_id'], s) for s in json.load(f))

        for c in self._cards.values():
            skill_id = c.active_skill_id
            s = self._skills[skill_id]
            name = s['name']
            description = s['clean_description']
            turn_max = s['turn_max']
            turn_min = s['turn_min']
            c.skill = Skill(name, description, self._expand_skill(skill_id),
                            turn_max, turn_min)

    def card(self, card_id):
        return self._cards[card_id]

    def _expand_skill(self, skill_id):
        s = self._skills[skill_id]

        if s['skill_type'] != MULTI_EFFECT_ID:
            return [parse_skill_effect(s['skill_type'], s['other_fields'])]

        return functools.reduce(list.__iadd__,
                                map(self._expand_skill, s['other_fields']),
                                [])

    def get_all_released_cards(self):
        return list(filter(
            lambda c: c.card_id <= 10000 and c.released_status,
            self._cards.values()))
