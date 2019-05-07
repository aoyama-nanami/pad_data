import dataclasses
import functools
import json

from pad_data import card, common, effect, skill_type, util

util.import_enum_members(common.EnemySkill, globals())

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
                    e = skill_type.parse(s['skill_type'], s['other_fields'])
                    effects.append(e)
                except Exception:
                    print(c.card_id, description, s, sep=' ')
                    raise
            _effect_post_process(effects)
            c.skill = card.Skill(
                name, clean_description, description, effects, turn_max,
                turn_min, raw_effects)

        for c in self._cards.values():
            card_id = c.card_id % 100000
            skills = []
            for ref in c.enemy_skill_refs:
                s = enemy_skills[ref['enemy_skill_id']]
                skills.append(s)
                if s['type'] == SKILL_SET:
                    for skill_id in filter(lambda x: x, s['params'][1:]):
                        skills.append(enemy_skills[skill_id])

            skills = [s for s in skills 
                      if s['type'] in
                      [VOID_SHIELD, ELEMENT_RESIST, TYPE_RESIST]]
            for skill in skills:
                skill_id = skill['enemy_skill_id']
                combined_skill_data = card.EnemyPassiveResist(
                    skill_id,
                    c.name,
                    skill['type'],
                    skill['name'],
                    skill['params'][1:],
                )
                if all(s.enemy_skill_id != skill_id for s in
                       self._cards[card_id].enemy_passive_resist):
                    self._cards[card_id].enemy_passive_resist.append(
                        combined_skill_data)

    def card(self, card_id):
        return self._cards[card_id]

    def _expand_skill(self, skill_id):
        s = self._skills[skill_id]

        if s['skill_type'] != skill_type.MULTI_EFFECT_ID:
            return [s]

        return functools.reduce(list.__iadd__,
                                map(self._expand_skill, s['other_fields']),
                                [])

    def get_all_released_cards(self):
        return list(filter(
            lambda c: c.card_id <= 10000 and c.released_status,
            self._cards.values()))

def _effect_post_process(effects):
    # merge repeated attacks into one instance
    for i, e in enumerate(effects):
        if isinstance(e, effect.AtkNuke):
            j = i + 1
            while j < len(effects) and e == effects[j]:
                j += 1
            if j - i == 1:
                continue
            merged_effect = dataclasses.replace(effects[i], repeat=j - i)
            effects[i:j] = [merged_effect]
            break

    # DoubleOrbChange -> OrbChange * 2
    for i, e in enumerate(effects):
        if isinstance(e, effect.DoubleOrbChange):
            effects[i:i + 1] = [
                effect.OrbChange([e.from1], [e.to1]),
                effect.OrbChange([e.from2], [e.to2]),
            ]
            break
