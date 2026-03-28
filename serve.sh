#!/bin/bash
set -e

pip install Pillow -q
python .github/workflows/build.py
echo "Open http://localhost:8080"
python -m http.server 8080 --directory html
