#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C.UTF-8 QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-offscreen} QT_QUICK_BACKEND=software
app=${1:-AusweisApp}
"$app" --version
set +e
timeout 15s "$app" --no-logfile > /tmp/ausweisapp-smoke.log 2>&1
status=$?
set -e
cat /tmp/ausweisapp-smoke.log
[[ $status == 124 ]] || { echo "Application exited unexpectedly: $status" >&2; exit 1; }
if grep -Eq 'failed to load component|is not installed|cannot load library|error while loading shared libraries|Unsupported image format|Error decoding' /tmp/ausweisapp-smoke.log; then
    echo 'Runtime dependency failure' >&2
    exit 1
fi
