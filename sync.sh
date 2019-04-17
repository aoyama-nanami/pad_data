#!/usr/bin/env bash
set -ex

mkdir -p data/raw
mkdir -p data/processed
gsutil -m rsync -r -c gs://mirubot-data/paddata/raw data/raw
gsutil -m rsync -r -c gs://mirubot-data/paddata/processed data/processed
