#!/usr/bin/env bash
set -euo pipefail
series=${1:?jammy, noble or resolute}
workspace=$(realpath -m "${2:?output workspace}")
repo=$(cd "$(dirname "$0")/../.." && pwd)
case "$series" in
    jammy) ubuntu=22.04; dockerfile=Dockerfile.portable ;;
    noble) ubuntu=24.04; dockerfile=Dockerfile.portable ;;
    resolute) ubuntu=26.04; dockerfile=Dockerfile.resolute ;;
    *) echo 'Unsupported Ubuntu series' >&2; exit 2 ;;
esac
version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["upstream_tag"])' "$repo/packaging/linux/release-lock.json")
mkdir -p "$workspace/logs"
docker build --build-arg "UBUNTU_VERSION=$ubuntu" -t "ausweisapp-build:$series" \
    -f "$repo/packaging/linux/$dockerfile" "$repo/packaging/linux"
args=(--series "$series" --output "$workspace/source-$series")
if [[ $series != resolute ]]; then
    args+=(--dependencies "$workspace/dependencies")
fi
python3 "$repo/packaging/linux/prepare-source.py" "${args[@]}"
docker run --rm --network none --user "$(id -u):$(id -g)" \
    -e HOME=/tmp -e "JOBS=${JOBS:-16}" -e "DEB_BUILD_OPTIONS=parallel=${JOBS:-16}" \
    -v "$workspace:/work" -w "/work/source-$series/ausweisapp-$version" \
    "ausweisapp-build:$series" bash -c \
    'dpkg-buildpackage -S -sa -us -uc -d && dpkg-buildpackage -b -us -uc' \
    2>&1 | tee "$workspace/logs/build-$series.log"
