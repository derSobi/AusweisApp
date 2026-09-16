#!/usr/bin/env bash
set -euo pipefail
app=${1:?application path}
export XDG_RUNTIME_DIR=/tmp/ausweisapp-wayland
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
export WAYLAND_DISPLAY=ausweisapp-test QT_QPA_PLATFORM=wayland QT_QUICK_BACKEND=software
weston --backend=headless-backend.so --socket="$WAYLAND_DISPLAY" --idle-time=0 \
    --use-pixman --log=/tmp/weston.log &
weston_pid=$!
trap 'kill "$weston_pid" 2>/dev/null || true' EXIT
for attempt in {1..50}; do
    [[ ! -S "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ]] || break
    kill -0 "$weston_pid"
    sleep 0.1
done
[[ -S "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ]] || { cat /tmp/weston.log; exit 1; }
APPIMAGE_EXTRACT_AND_RUN=1 "$(dirname "$0")/smoke-test.sh" "$app"
