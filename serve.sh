#!/bin/bash
set -e

python3 -m pip install Pillow -q
python3 .github/workflows/build.py
echo "Open http://localhost:8080"
python3 -m http.server 8080 --directory html
