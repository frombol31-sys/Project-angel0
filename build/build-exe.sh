#!/usr/bin/env bash
# Builds GoreZone.exe (Windows 10/11, 64-bit): a native game window (WebView2) with the game inside.
# Needs: Go, python3 + Pillow, rsrc (go install github.com/akavel/rsrc@latest). Usage: build/build-exe.sh [outdir]
set -euo pipefail
cd "$(dirname "$0")/desktop"
OUT=${1:-../out}; mkdir -p "$OUT"
rm -rf web && python3 ../make-app-assets.py ../../game web
python3 -c "from PIL import Image; Image.open('web/icon-512.png').save('icon.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
RSRC=$(command -v rsrc || echo "$(go env GOPATH)/bin/rsrc")
"$RSRC" -manifest app.manifest -ico icon.ico -arch amd64 -o rsrc_windows_amd64.syso
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags "-s -w -H windowsgui" -o "$OUT/GoreZone.exe" .
echo "OK: $OUT/GoreZone.exe"
