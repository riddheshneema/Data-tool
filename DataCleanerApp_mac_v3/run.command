#!/bin/bash
set -e
cd "$(dirname "$0")"

# Find Python 3.11
PY311=""
if command -v python3.11 >/dev/null 2>&1; then
  PY311="$(command -v python3.11)"
elif [ -x "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11" ]; then
  PY311="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11"
elif [ -x "/usr/local/bin/python3.11" ]; then
  PY311="/usr/local/bin/python3.11"
fi

if [ -z "$PY311" ] ; then
  echo "🚫 Python 3.11 not found. Please install Python 3.11 from python.org, then re-run."
  exit 1
fi

echo "✅ Using Python at: $PY311"

# Create venv if missing
if [ ! -d ".venv" ]; then
  "$PY311" -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Upgrade pip and install deps
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start the local web app
python -m streamlit run app.py --server.port 8501 --server.headless true
