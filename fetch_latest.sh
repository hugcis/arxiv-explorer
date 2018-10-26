#!/bin/sh

oai-harvest -s cs -d data -p arXiv -f $(date -v-5d +%Y-%m-%d) http://export.arxiv.org/oai2
python tidy_files.py
curl http://127.0.0.1:8000/api/dbfill/

