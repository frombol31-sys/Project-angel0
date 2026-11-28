#!/usr/bin/env bash
# OBSOLETE: builds a targetSdk 23 APK that Android 15+ refuses to install. Use build/build-apk36.sh or the CI workflow.
# Builds GoreZone.apk without Android Studio.
# Needs (Ubuntu): apt install aapt apksigner zipalign dalvik-exchange android-sdk-platform-23 default-jdk
set -euo pipefail
cd "$(dirname "$0")/android"
JAR=/usr/lib/android-sdk/platforms/android-23/android.jar
OUT=${1:-../out}
rm -rf gen obj assets/* stage && mkdir -p gen obj stage "$OUT"
python3 ../make-app-assets.py ../../game assets
cp ../../game/icon-192.png res/mipmap/ic_launcher.png
aapt package -f -M AndroidManifest.xml -S res -A assets -I "$JAR" -J gen -F stage/app.unsigned.apk
javac -Xlint:-options --release 8 -classpath "$JAR" -d obj src/com/gorezone/game/MainActivity.java $(find gen -name R.java) 2>&1 | grep -v "Picked up" || true
dalvik-exchange --dex --output=stage/classes.dex obj
(cd stage && aapt add app.unsigned.apk classes.dex >/dev/null)
zipalign -f 4 stage/app.unsigned.apk stage/app.aligned.apk
KS=${KEYSTORE:-../gorezone-release.jks}
[ -f "$KS" ] || keytool -genkeypair -keystore "$KS" -alias gorezone -keyalg RSA -keysize 2048 -validity 10000 -storepass gorezone -keypass gorezone -dname "CN=GORE ZONE" >/dev/null 2>&1
apksigner sign --ks "$KS" --ks-pass pass:gorezone --key-pass pass:gorezone --ks-key-alias gorezone --out "$OUT/GoreZone.apk" stage/app.aligned.apk
apksigner verify "$OUT/GoreZone.apk" && echo "OK: $OUT/GoreZone.apk"
