import dataclasses
import functools
import json

from pad_data import card, effect, skill_type

class Database:
    def __init__(self, raw_cards_json='data/processed/jp_raw_cards.json',
                 skills_json='data/processed/jp_skills.json'):
        with open(raw_cards_json, 'r') as f:
            self._cards = dict(
                (c['card_id'], card.Card(c)) for c in json.load(f))

        with open(skills_json, 'r') as f:
            self._skills = dict((s['skill_id'], s) for s in json.load(f))

        for c in self._cards.values():
            raw_effects = self._expand_skill(c.active_skill_id)
            name = raw_effects[0]['name']
            description = raw_effects[0]['clean_description']
            turn_max = raw_effects[0]['turn_max']
            turn_min = raw_effects[0]['turn_min']
            effects = [skill_type.parse(s['skill_type'], s['other_fields'])
                       for s in raw_effects
                       if s['skill_type'] != skill_type.MULTI_EFFECT_ID]
            _effect_post_process(effects)
            c.skill = card.Skill(
                name, description, effects, turn_max, turn_min, raw_effects)

    def card(self, card_id):
        return self._cards[card_id]

    def _expand_skill(self, skill_id):
        s = self._skills[skill_id]

        if s['skill_type'] != skill_type.MULTI_EFFECT_ID:
            return [s]

        return functools.reduce(list.__iadd__,
                                map(self._expand_skill, s['other_fields']),
                                [s])

    def get_all_released_cards(self):
        return list(filter(
            lambda c: c.card_id <= 10000 and c.released_status,
            self._cards.values()))

def _effect_post_process(effects):
    # merge repeated attacks into one instance
    for i in range(len(effects)):
        if isinstance(effects[i], effect.AtkNuke):
            j = i + 1
            while j < len(effects) and effects[i] == effects[j]:
                j += 1
            if j - i == 1:
                continue
            merged_effect = dataclasses.replace(effects[i], repeat=j - i)
            effects[i:j] = [merged_effect]
            break

    # DoubleOrbChange -> OrbChange * 2
    for i in range(len(effects)):
        if isinstance(effects[i], effect.DoubleOrbChange):
            e = effects[i]
            effects[i:i + 1] = [
                effect.OrbChange([e.from1], [e.to1]),
                effect.OrbChange([e.from2], [e.to2]),
            ]
            break
