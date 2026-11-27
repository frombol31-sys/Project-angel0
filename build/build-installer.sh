#!/usr/bin/env bash
# Builds GoreZone-Setup.exe (Windows installer) around GoreZone.exe. Needs: nsis (makensis). Usage: build/build-installer.sh [outdir]
set -euo pipefail
cd "$(dirname "$0")"
OUT=$(realpath -m "${1:-out}"); mkdir -p "$OUT"
./build-exe.sh "$OUT"
cd desktop
makensis -V2 -DOUTFILE="$OUT/GoreZone-Setup.exe" -DEXEFILE="$OUT/GoreZone.exe" installer.nsi
echo "OK: $OUT/GoreZone-Setup.exe"
