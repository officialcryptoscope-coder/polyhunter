#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install -y python git
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
chmod +x polyhunter.py
mkdir -p "$HOME/.polyhunter/keystores"
chmod 700 "$HOME/.polyhunter" "$HOME/.polyhunter/keystores" 2>/dev/null || true
echo "Installed. Start with: python polyhunter.py"
