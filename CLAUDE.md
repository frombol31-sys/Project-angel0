# GORE ZONE — working notes

## Release deliverables (owner's standing rule)
When a new version is built, deliver ONLY:
- the Android APK (`build/build-apk36.sh`, bump `VERSION_CODE`);
- the Windows installer `GoreZone-Setup.exe` (`build/build-installer.sh`);
- the claude.ai artifact update (`build/make-artifact.py`).

NEVER build or send:
- the web version (`GoreZone-web.zip`);
- the bare `GoreZone.exe` without the installer (it is only an intermediate file of the installer build — do not send it).

## Developer edition
- `GZ_DEV=1` before `build/build-apk36.sh` → `GoreZone-Dev.apk` (package `com.gorezone.game.dev`, label "GORE ZONE Dev", installs next to the normal game).
- `GZ_DEV=1 build/build-installer.sh` → `GoreZone-Dev-Setup.exe` (installs as "GORE ZONE Dev").
- Dev artifact: the normal artifact page with `<script>window.GZ_DEV = 1;</script>` prepended and the title "GORE ZONE Dev". `?dev=1` in the URL also turns the panel on.
- In game: DEV button / F1 / backquote opens the dev panel (cheats, spawning, time speed, stats).
