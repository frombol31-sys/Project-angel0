# GORE ZONE — working notes

## Release deliverables (owner's standing rule)
When a new version is built, deliver ONLY:
- the Android APK (`build/build-apk36.sh`, bump `VERSION_CODE`);
- the Windows installer `GoreZone-Setup.exe` (`build/build-installer.sh`);
- the claude.ai artifact update (`build/make-artifact.py`).

NEVER build or send:
- the web version (`GoreZone-web.zip`);
- the bare `GoreZone.exe` without the installer (it is only an intermediate file of the installer build — do not send it).
