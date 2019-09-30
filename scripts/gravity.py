#! /usr/bin/env python3

'''A tool to calculate best combination of 100% gravity'''

import collections

import path_common # pylint: disable=import-error,unused-import

from pad_data import database, filters
from pad_data.active_skill import effect as as_effect

class Item:
    def __init__(self, c):
        self.card = c
        self.name = c.name
        self.turn = c.skill.turn_min
        self.count = 10
        self.gravity = 0
        self.true_gravity = 0

        for e in c.skill.effects:
            if isinstance(e, as_effect.Gravity):
                self.gravity = e.percentage
            elif isinstance(e, as_effect.TrueGravity):
                self.true_gravity = e.percentage

    def dump(self):
        self.card.dump(print_leader_skill=0, print_active_skill=1)

def killable(team, cards, turn):
    gravity = 1
    true_gravity = 0

    for (t, c) in zip(team, cards):
        cd = t + c.turn
        cast = turn // cd
        gravity *= (1 - c.gravity / 100) ** cast
        true_gravity += c.true_gravity / 100 * cast

    return true_gravity >= gravity

def available(cards):
    count = collections.defaultdict(int)
    for c in cards:
        count[c.name] += 1
    return all(count[c.name] <= c.count for c in cards)

def optimize(cards, team, current):
    if len(team) == len(current):
        turn = max(team[i] + current[i].turn
                   for i in range(len(team)))
        if not killable(team, current, turn) or not available(current):
            return 9999, []
        return turn, current.copy()

    last_cd = current[-1].turn if current else 9999
    best_turn, best_assists = 9999, []
    for c in cards:
        if c.turn > last_cd:
            continue

        current.append(c)
        t, a = optimize(cards, team, current)
        current.pop()
        if t < best_turn:
            best_turn, best_assists = t, a
    return best_turn, best_assists

def box_override(c):
    del c['壮絶の降魔神・降三世明王']
    del c['転生降三世明王']
    del c['双冥剣グラビティア']
    del c['チャンドラ・ナラー']
    c['神王妃・ミニへら'].count = 1
    c['閃光の冒険野郎ヴァン・クロウ'].count = 1
    c['影ナル者'].count = 1

# pylint: disable=undefined-variable
def main():
    db = database.Database()
    cards = db.get_all_released_cards()

    cards = filter((filters.Skill(as_effect.Gravity, '1') |
                    filters.Skill(as_effect.TrueGravity, '1')) &
                   filters.INHERITABLE,
                   cards)
    cards = {c.skill.name: Item(c) for c in cards}
    cards = {c.name: c for c in cards.values()}
    box_override(cards)

    turn, assists = optimize(cards.values(), [0, 0, 0, 15, 16], [])
    print(f'turn = {turn}')
    for c in assists:
        c.dump()

if __name__ == '__main__':
    main()
