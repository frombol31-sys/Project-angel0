#!/usr/bin/env bash
# Builds an installable GoreZone.apk (target API 36, min 24) from android/ WITHOUT the Android SDK or Gradle.
# The framework (classes + resources) comes from Robolectric's android-all jar on Maven Central.
# Needs (Ubuntu): aapt2 apksigner zipalign dalvik-exchange default-jdk python3 curl
# Usage: KEYSTORE=upload.jks KS_PASS=... KEY_ALIAS=upload [VERSION_CODE=N] build/build-apk36.sh [outdir]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=$(mkdir -p "${1:-$ROOT/build/out}" && cd "${1:-$ROOT/build/out}" && pwd)
W=${WORK:-$ROOT/build/.apk36}; mkdir -p "$W"
ALL=$W/android-all-36.jar
[ -s "$ALL" ] || curl -fsSL -o "$ALL" https://repo1.maven.org/maven2/org/robolectric/android-all/16-robolectric-13921718-2/android-all-16-robolectric-13921718-2.jar
# aapt2 only needs the framework manifest + resource table. Debian's aapt2 can't read the API 36 table,
# so resources link against API 34 (has every attribute the manifest uses); code compiles against API 36.
RES=$W/android-all-34.jar
[ -s "$RES" ] || curl -fsSL -o "$RES" https://repo1.maven.org/maven2/org/robolectric/android-all/14-robolectric-10818077/android-all-14-robolectric-10818077.jar
[ -s "$W/android.jar" ] || (cd "$W" && rm -rf fw && mkdir fw && cd fw && unzip -q "$RES" AndroidManifest.xml resources.arsc && zip -q -0 ../android.jar AndroidManifest.xml resources.arsc)
APP=$ROOT/android/app/src/main
rm -rf "$W/stage" && mkdir -p "$W/stage/res" "$W/stage/obj" "$W/stage/assets"
python3 "$ROOT/build/make-app-assets.py" "$ROOT/game" "$W/stage/assets"
sed 's|<manifest |<manifest package="com.gorezone.game" |' "$APP/AndroidManifest.xml" > "$W/stage/AndroidManifest.xml"
aapt2 compile --dir "$APP/res" -o "$W/stage/res"
VC=${VERSION_CODE:?set VERSION_CODE (CI builds use 300+run number; pick a higher one or use the CI build)}
aapt2 link -o "$W/stage/app.unsigned.apk" -I "$W/android.jar" --manifest "$W/stage/AndroidManifest.xml" -R "$W"/stage/res/*.flat -A "$W/stage/assets" \
  --min-sdk-version 24 --target-sdk-version 36 --version-code "$VC" --version-name "${VERSION_NAME:-1.0.$VC}" \
  --java "$W/stage/gen" -0 js -0 html
javac -Xlint:-options --release 8 -classpath "$ALL" -d "$W/stage/obj" \
  $(find "$APP/java" -name '*.java') $(find "$W/stage/gen" -name R.java) 2>&1 | grep -v "Picked up" || true
dalvik-exchange --dex --min-sdk-version=24 --output="$W/stage/classes.dex" "$W/stage/obj"
(cd "$W/stage" && zip -q -j app.unsigned.apk classes.dex)
zipalign -f -p 4 "$W/stage/app.unsigned.apk" "$W/stage/app.aligned.apk"
apksigner sign --ks "${KEYSTORE:?set KEYSTORE}" --ks-pass "pass:${KS_PASS:?set KS_PASS}" --ks-key-alias "${KEY_ALIAS:-upload}" \
  --key-pass "pass:${KEY_PASS:-$KS_PASS}" --out "$OUT/GoreZone.apk" "$W/stage/app.aligned.apk"
apksigner verify "$OUT/GoreZone.apk" && echo "OK: $OUT/GoreZone.apk (versionCode $VC)"
