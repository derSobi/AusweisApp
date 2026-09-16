#!/usr/bin/env python3
"""Preserve Qt and bundled third-party license texts with their source paths."""
from pathlib import Path
import shutil
root = Path('qt')
dest = Path('debian/ausweisapp/usr/share/doc/ausweisapp/third-party/qt')
for source in root.rglob('*'):
    if not source.is_file():
        continue
    name = source.name.lower()
    if name.startswith(('license', 'licence', 'copying', 'copyright')) or name == 'reuse.toml':
        target = dest / source.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
