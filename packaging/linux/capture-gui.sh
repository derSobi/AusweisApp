#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C.UTF-8 QT_QUICK_BACKEND=software
out=${1:?output directory}
mkdir -p "$out"
AusweisApp --no-logfile > "$out/gui.log" 2>&1 &
app_pid=$!
trap 'kill "$app_pid" 2>/dev/null || true' EXIT
sleep 8
kill -0 "$app_pid"
import -window root "$out/gui.png"
