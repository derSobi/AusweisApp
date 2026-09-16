#!/usr/bin/env python3
"""Verify downloaded upstream sources and extract only required Qt modules."""
import hashlib
import pathlib
import sys
import tarfile

root = pathlib.Path(sys.argv[1]).resolve()
dest = pathlib.Path(sys.argv[2]).resolve()
inputs = {
    'qt-everywhere-src-6.10.2.tar.xz': ('c3df0f0e421130cc52ed81cb712358804471ce9bd2a41d97828f9f5b1bf7fed2', 'qt'),
    'llhttp-9.4.2.tar.gz': ('ba717a2f99f340a0ee9796aaf2b1acca057e1e37682ffd2bc4def4d3b6bc4005', 'llhttp'),
    'cmake-3.31.6.tar.gz': ('653427f0f5014750aafff22727fb2aa60c6c732ca91808cfb78ce22ddd9e55f0', 'cmake-bootstrap'),
}
modules = {'qtbase', 'qtdeclarative', 'qttools', 'qtshadertools', 'qtlanguageserver',
           'qtsvg', 'qtwebsockets', 'qtscxml', 'qtwayland', 'qttranslations', 'cmake', 'coin'}
for filename, (expected, component) in inputs.items():
    path = root / filename
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    if digest != expected:
        raise SystemExit(f'SHA256 mismatch: {filename}: {digest}')
    target = dest / component
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path) as archive:
        for entry in archive:
            parts = pathlib.PurePosixPath(entry.name).parts
            if len(parts) < 2:
                continue
            if component == 'qt' and len(parts) > 2 and parts[1] not in modules:
                continue
            if component == 'qt' and len(parts) == 2 and entry.isdir() and parts[1] not in modules:
                continue
            entry.name = str(pathlib.PurePosixPath(*parts[1:]))
            archive.extract(entry, target, filter='data')
    print(f'{component}: verified and extracted', flush=True)
