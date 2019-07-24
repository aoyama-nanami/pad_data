#! /usr/bin/env python3

import itertools
import json
from pad_data import database

JSON_PATH = 'html/data/jp_cards_merged.json'

def print_old(s, do_print):
    if do_print:
        print(f'\x1b[31m{s}\x1b[m')

def print_new(s, do_print):
    if do_print:
        print(f'\x1b[32m{s}\x1b[m')

def print_common(s):
    print(f'\x1b[33m{s}\x1b[m')

def zip_by_card_id(list_new, list_old):
    i_new, i_old = 0, 0
    while i_new < len(list_new) or i_old < len(list_old):
        if i_new >= len(list_new):
            yield None, list_old[i_old]
            i_old += 1
        elif i_old >= len(list_old):
            yield list_new[i_new], None
            i_new += 1
        elif list_old[i_old]['card_id'] < list_new[i_new]['card_id']:
            yield None, list_old[i_old]
            i_old += 1
        elif list_old[i_old]['card_id'] > list_new[i_new]['card_id']:
            yield list_new[i_new], None
            i_new += 1
        else:
            yield list_new[i_new], list_old[i_old]
            i_old += 1
            i_new += 1

def maybe_remove_newline(x):
    if isinstance(x, str):
        return x.replace('\n', '')
    else:
        return x

def diff_one(new, old, indent_level):
    if new is None:
        new = {}
    if old is None:
        old = {}
    indent = ' ' * (indent_level * 2)

    keys = set(new.keys()) | set(old.keys())
    sorted_keys = []
    # put card id and name at beginning
    if 'card_id' in keys:
        keys.remove('card_id')
        sorted_keys.append('card_id')
    keys.remove('name')
    sorted_keys.append('name')
    sorted_keys += sorted(list(keys))

    for k in sorted_keys:
        v_new = new.get(k, None)
        v_old = old.get(k, None)
        if (k == 'card_id' or k == 'name') and v_old == v_new:
            print_common(f'{indent}"{k}": {v_old}')
        elif v_old != v_new:
            if k == 'skill' or k == 'leader_skill':
                print_old(f'{indent}"{k}": {{', v_old)
                print_new(f'{indent}"{k}": {{', v_new)
                diff_one(v_new, v_old, indent_level + 1)
                print_old(f'{indent}}}', v_old)
                print_new(f'{indent}}}', v_new)
            else:
                print_old(f'{indent}"{k}": {maybe_remove_newline(v_old)}',
                          v_old)
                print_new(f'{indent}"{k}": {maybe_remove_newline(v_new)}',
                          v_new)

def diff(list_new, list_old):
    for (new, old) in zip_by_card_id(list_new, list_old):
        if new != old:
            print_common('{')
            diff_one(new, old, 1)
            print_common('}')

def main():
    db = database.Database()
    cards = db.get_all_released_cards()
    new = list(map(lambda c: c.merged_json, cards))
    new = json.loads(json.dumps(new))
    with open(JSON_PATH, 'r') as f:
        old = json.load(f)
    diff(new, old)
    with open(JSON_PATH, 'w') as f:
        json.dump(list(map(lambda c: c.merged_json, cards)), f,
                  separators=(',', ':'),
                  ensure_ascii=False)

if __name__ == '__main__':
    main()
