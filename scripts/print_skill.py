#! /usr/bin/env python3

import sys

import path_common # pylint: disable=import-error,unused-import

from pad_data import database


def main() -> None:
    card_id = int(sys.argv[1])

    db = database.Database()
    card = db.card(card_id)
    print(card.skill)
    db.print_raw_skills(card.active_skill_id)
    print()

    print(card.leader_skill)
    db.print_raw_skills(card.leader_skill_id)
    print()

if __name__ == '__main__':
    main()
