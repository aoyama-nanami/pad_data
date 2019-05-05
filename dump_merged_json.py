#! /usr/bin/env python3

import json
from pad_data import database

def main():
    db = database.Database()
    cards = db.get_all_released_cards()
    with open('html/data/jp_cards_merged.json', 'w') as f:
        json.dump(list(map(lambda c: c.merged_json, cards)), f)

if __name__ == '__main__':
    main()
