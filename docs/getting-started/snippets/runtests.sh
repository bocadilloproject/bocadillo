#!/usr/bin/env bash
# 1. Run server in background
# 2. Run pytest
# 3. Kill api.py when pytest terminates.
python api.py & pytest test.py; kill $!
