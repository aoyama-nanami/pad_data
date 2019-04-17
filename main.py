#! /usr/bin/env python3

from pad_data.database import Database

def main():
    db = Database()
    print(db.card(5229))
main()
