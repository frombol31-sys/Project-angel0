#!/usr/bin/env bash
# Builds GoreZone.exe (Windows, 64-bit) with Go. Usage: build/build-exe.sh [outdir]
set -euo pipefail
cd "$(dirname "$0")/desktop"
OUT=${1:-../out}; mkdir -p "$OUT"
rm -rf web && python3 ../make-app-assets.py ../../game web
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -o "$OUT/GoreZone.exe" .
echo "OK: $OUT/GoreZone.exe"
