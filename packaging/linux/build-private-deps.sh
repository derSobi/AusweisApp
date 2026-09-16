#!/usr/bin/env bash
set -euo pipefail
src=$(realpath "${1:?source directory}")
build=$(realpath -m "${2:?build directory}")
jobs=${JOBS:-4}
mkdir -p "$build"
cmake_bin=${CMAKE:-cmake}
if ! "$cmake_bin" --version | head -1 | awk '{split($3,v,"."); exit !(v[1]>3 || (v[1]==3 && v[2]>=25))}'; then
    /usr/bin/cmake -S "$src/cmake-bootstrap" -B "$build/cmake-build" -GNinja \
        -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
        -DCMAKE_INSTALL_PREFIX="$build/cmake"
    /usr/bin/cmake --build "$build/cmake-build" --parallel "$jobs"
    /usr/bin/cmake --install "$build/cmake-build"
    cmake_bin="$build/cmake/bin/cmake"
fi
export PATH="$(dirname "$cmake_bin"):$PATH"
"$cmake_bin" -S "$src/llhttp" -B "$build/llhttp" -GNinja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DLLHTTP_BUILD_SHARED_LIBS=OFF -DLLHTTP_BUILD_STATIC_LIBS=ON \
    -DCMAKE_INSTALL_PREFIX="$build/prefix"
"$cmake_bin" --build "$build/llhttp" --parallel "$jobs"
"$cmake_bin" --install "$build/llhttp"
mkdir -p "$build/qt"
cd "$build/qt"
if [[ ! -f CMakeCache.txt ]]; then
    "$src/qt/configure" -prefix /usr/lib/ausweisapp/qt6 \
        -release -shared -opensource -confirm-license -nomake examples -nomake tests \
        -submodules qtbase,qtdeclarative,qttools,qtsvg,qtwebsockets,qtscxml,qtwayland,qttranslations \
        -no-feature-assistant -no-feature-designer -no-feature-qdoc \
        -openssl-linked -no-icu -qt-harfbuzz -system-libpng -system-libjpeg
fi
"$cmake_bin" --build . --parallel "$jobs"
DESTDIR="$build/prefix" "$cmake_bin" --install .
