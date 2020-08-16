#!/usr/bin/env bash
set -ex

data/downloader/downloader.py

scripts/dump_merged_json.py

if ! git diff --quiet html/data/jp_cards_merged.json; then
  make test &&
  git commit -m "data: $(date +%Y%m%d) update" -- html/data/jp_cards_merged.json
fi
