#!/usr/bin/env python3
"""Download public build inputs and reject any content outside the pinned lock."""
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
lock = json.loads((Path(__file__).with_name('release-lock.json')).read_text())
urls = {
 'runtime-x86_64': 'https://github.com/AppImage/type2-runtime/releases/download/continuous/runtime-x86_64',
 f"AusweisApp-{lock['upstream_tag']}.tar.gz": f"https://github.com/Governikus/AusweisApp/releases/download/{lock['upstream_tag']}/AusweisApp-{lock['upstream_tag']}.tar.gz",
 'qt-everywhere-src-6.10.2.tar.xz': 'https://download.qt.io/archive/qt/6.10/6.10.2/single/qt-everywhere-src-6.10.2.tar.xz',
 'llhttp-9.4.2.tar.gz': 'https://github.com/nodejs/llhttp/archive/refs/tags/release/v9.4.2.tar.gz',
 'cmake-3.31.6.tar.gz': 'https://github.com/Kitware/CMake/releases/download/v3.31.6/cmake-3.31.6.tar.gz',
 'linuxdeploy-x86_64.AppImage': 'https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage',
 'linuxdeploy-plugin-qt-x86_64.AppImage': 'https://github.com/linuxdeploy/linuxdeploy-plugin-qt/releases/download/continuous/linuxdeploy-plugin-qt-x86_64.AppImage',
}
for filename, url in urls.items():
    target = out / filename
    temporary = target.with_suffix(target.suffix + '.partial')
    candidate = target
    if not target.exists():
        request = urllib.request.Request(url, headers={'User-Agent': 'AusweisApp-local-build'})
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open('wb') as f:
            import shutil
            shutil.copyfileobj(response, f)
        candidate = temporary
    with candidate.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    if digest != lock['files'][filename]['sha256']:
        raise SystemExit(f'Checksum mismatch: {filename}; review upstream change before updating the lock.')
    if candidate == temporary:
        temporary.replace(target)
    if filename.endswith('.AppImage'):
        target.chmod(0o755)
    print(f'OK {filename}', flush=True)
