#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
command -v python >/dev/null 2>&1 || pkg install -y python
python -m pip install --upgrade pip
chmod +x polyhunter.py
echo "PolyHunter ready. Run: python polyhunter.py --help"
