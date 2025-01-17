#!/bin/bash

pip install -r requirements.txt
PG_DSN="postgresql://rockwell:rockwell@localhost:5432/rockwell" python3 srvc_restream.py
