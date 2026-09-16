#!/usr/bin/env bash
set -euo pipefail
appimage=$(realpath "${1:?AppImage path}")
logs=$(realpath -m "${2:?log output directory}")
scripts=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$logs"
for version in 22.04 24.04 26.04; do
    docker run --rm -v "$appimage:/app/AusweisApp.AppImage:ro" \
        -v "$scripts:/scripts:ro" "ubuntu:$version" bash -c \
        'apt-get update -qq && apt-get install -y --no-install-recommends ca-certificates libgl1 libopengl0 libegl1 libfontconfig1 libdbus-1-3 libglib2.0-0 && APPIMAGE_EXTRACT_AND_RUN=1 /scripts/smoke-test.sh /app/AusweisApp.AppImage' \
        > "$logs/appimage-$version.log" 2>&1
    echo "PASS Ubuntu $version"
done
