#!/usr/bin/env bash
set -ex

cd "$(dirname "$0")"

mkdir -p data/raw/jp
mkdir -p data/processed
gsutil -m rsync -r -c gs://mirubot-data/paddata/raw/jp data/raw/jp
gsutil -m rsync -r -c -x '(?!jp_).*' \
    gs://mirubot-data/paddata/processed data/processed

scripts/dump_merged_json.py

git commit -m "data: $(date +%Y%m%d) update" -- html/data/jp_cards_merged.json
# TODO: determine if it's better to have auto push
