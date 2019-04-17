import json
from .common import Card, Skill

class Database:
    def __init__(self, raw_cards_json='data/processed/jp_raw_cards.json',
                 skills_json='data/processed/jp_skills.json'):
        with open(raw_cards_json, 'r') as f:
            self._cards = dict((c['card_id'], Card(c)) for c in json.load(f))

        with open(skills_json, 'r') as f:
            self._skills = \
                dict((s['skill_id'], Skill(s)) for s in json.load(f))

    def card(self, card_id):
        return self._cards[card_id]

    def get_all_released_cards(self):
        return list(filter(
            lambda c: c.card_id <= 10000 and c.released_status,
            self._cards.values()))
