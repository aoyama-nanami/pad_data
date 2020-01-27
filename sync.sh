#!/usr/bin/env bash
set -ex

cd "$(dirname "$0")"

mkdir -p data/raw/jp
mkdir -p data/processed
gsutil -m rsync -r -c gs://mirubot-data/paddata/raw/jp data/raw/jp
gsutil -m rsync -r -c -x '(?!jp_).*' \
    gs://mirubot-data/paddata/processed data/processed

scripts/dump_merged_json.py

if ! git diff --quiet html/data/jp_cards_merged.json; then
  make test &&
  git commit -m "data: $(date +%Y%m%d) update" -- html/data/jp_cards_merged.json
fi
