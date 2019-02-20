#!/usr/bin/env bash
# 1. Run server in background
# 2. Run pytest
# 3. Kill app.py when pytest terminates.
python app.py & pytest test.py; kill $!
