; GORE ZONE installer (NSIS). Built by build/build-installer.sh
Unicode true
!include "MUI2.nsh"

!define APPNAME "GORE ZONE"
!define APPVER "1.0"
!define UNINSTKEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\GoreZone"

Name "${APPNAME}"
OutFile "${OUTFILE}"
InstallDir "$PROGRAMFILES64\GORE ZONE"
InstallDirRegKey HKLM "Software\GoreZone" "InstallDir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
BrandingText "${APPNAME} ${APPVER}"

!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN "$INSTDIR\GoreZone.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Запустить GORE ZONE"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Russian"

Section "GORE ZONE" SecMain
  SetOutPath "$INSTDIR"
  File "${EXEFILE}"
  File "icon.ico"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateDirectory "$SMPROGRAMS\GORE ZONE"
  CreateShortcut "$SMPROGRAMS\GORE ZONE\GORE ZONE.lnk" "$INSTDIR\GoreZone.exe" "" "$INSTDIR\icon.ico"
  CreateShortcut "$SMPROGRAMS\GORE ZONE\Удалить GORE ZONE.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\GORE ZONE.lnk" "$INSTDIR\GoreZone.exe" "" "$INSTDIR\icon.ico"
  WriteRegStr HKLM "Software\GoreZone" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "${UNINSTKEY}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "${UNINSTKEY}" "DisplayVersion" "${APPVER}"
  WriteRegStr HKLM "${UNINSTKEY}" "Publisher" "GORE ZONE"
  WriteRegStr HKLM "${UNINSTKEY}" "DisplayIcon" "$INSTDIR\icon.ico"
  WriteRegStr HKLM "${UNINSTKEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${UNINSTKEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKLM "${UNINSTKEY}" "NoModify" 1
  WriteRegDWORD HKLM "${UNINSTKEY}" "NoRepair" 1
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\GoreZone.exe"
  Delete "$INSTDIR\icon.ico"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  Delete "$SMPROGRAMS\GORE ZONE\GORE ZONE.lnk"
  Delete "$SMPROGRAMS\GORE ZONE\Удалить GORE ZONE.lnk"
  RMDir "$SMPROGRAMS\GORE ZONE"
  Delete "$DESKTOP\GORE ZONE.lnk"
  DeleteRegKey HKLM "${UNINSTKEY}"
  DeleteRegKey HKLM "Software\GoreZone"
SectionEnd
