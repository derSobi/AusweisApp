#!/usr/bin/env bash
set -euo pipefail
# Run inside the Jammy build image, with this workspace mounted at /work.
scripts=$(cd "$(dirname "$0")" && pwd)
workspace=${1:?workspace containing the portable deb, tools and Qt prefix}
package=${2:?path to the Jammy .deb}
qt=${3:?path to the installed private Qt prefix}
version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["upstream_tag"])' "$scripts/release-lock.json")
appdir="$workspace/AppDir"
[[ ! -e "$appdir" ]] || { echo "Refusing to overwrite $appdir" >&2; exit 1; }
mkdir -p "$appdir"
dpkg-deb -x "$package" "$appdir"
# linuxdeploy gathers the required Qt runtime from the verified prefix.
# Keep the Debian license notices, but avoid a duplicate private Qt tree.
rm -rf "$appdir/usr/lib/ausweisapp/qt6"
export APPIMAGE_EXTRACT_AND_RUN=1
export PATH="$workspace/tools:$qt/bin:$PATH"
export QMAKE="$qt/bin/qmake"
export LD_LIBRARY_PATH="$qt/lib"
export QML_SOURCES_PATHS="$workspace/source-jammy/ausweisapp-$version/src/ui/qml"
export EXTRA_PLATFORM_PLUGINS='libqoffscreen.so;libqwayland.so'
export EXTRA_QT_MODULES='svg;waylandcompositor'
export LDAI_RUNTIME_FILE="$workspace/tools/runtime-x86_64"
export LDAI_OUTPUT="$workspace/AusweisApp-$version-x86_64.AppImage"
ln -sf linuxdeploy-plugin-qt-x86_64.AppImage "$workspace/tools/linuxdeploy-plugin-qt"
"$workspace/tools/linuxdeploy-x86_64.AppImage" --appdir "$appdir" \
    --executable "$appdir/usr/bin/AusweisApp" \
    --desktop-file "$appdir/usr/share/applications/com.governikus.ausweisapp2.desktop" \
    --icon-file "$appdir/usr/share/icons/hicolor/scalable/apps/AusweisApp.svg" \
    --custom-apprun "$scripts/AppRun" --plugin qt --output appimage
