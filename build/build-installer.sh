#!/usr/bin/env bash
# Builds GoreZone-Setup.exe (Windows installer) around GoreZone.exe. Needs: nsis (makensis). Usage: build/build-installer.sh [outdir]
# GZ_DEV=1 builds the developer edition instead: GoreZone-Dev-Setup.exe, installs as "GORE ZONE Dev" next to the normal game.
set -euo pipefail
cd "$(dirname "$0")"
OUT=$(realpath -m "${1:-out}"); mkdir -p "$OUT"
if [ -n "${GZ_DEV:-}" ]; then EXEDIR="$OUT/.dev-exe"; SETUP="$OUT/GoreZone-Dev-Setup.exe"; DEFS=(-DAPPNAME="GORE ZONE Dev" -DAPPID=GoreZoneDev)
else EXEDIR="$OUT"; SETUP="$OUT/GoreZone-Setup.exe"; DEFS=(); fi
mkdir -p "$EXEDIR"
./build-exe.sh "$EXEDIR"
cd desktop
makensis -V2 "${DEFS[@]}" -DOUTFILE="$SETUP" -DEXEFILE="$EXEDIR/GoreZone.exe" installer.nsi
echo "OK: $SETUP"
