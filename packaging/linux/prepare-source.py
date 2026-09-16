#!/usr/bin/env python3
"""Create unsigned Debian source work trees. Never publishes or signs."""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import tarfile
import re
from versioning import package_version

p = argparse.ArgumentParser()
p.add_argument('--series', choices=['jammy', 'noble', 'resolute'], required=True)
p.add_argument('--output', type=pathlib.Path, required=True)
p.add_argument('--dependencies', type=pathlib.Path)
p.add_argument('--archive', type=pathlib.Path)
a = p.parse_args()
repo = pathlib.Path(__file__).resolve().parents[2]
lock = json.loads((repo / 'packaging/linux/release-lock.json').read_text())
version = lock['upstream_tag']
ubuntu = {'jammy': '22.04', 'noble': '24.04', 'resolute': '26.04'}[a.series]
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
tree = out / f'ausweisapp-{version}'
if tree.exists():
    raise SystemExit(f'Refusing to overwrite {tree}')
archive = out / f'ausweisapp_{version}.orig.tar.gz'
# The upstream archive supplied by the user is validated separately against the tag.
original = a.archive or (repo.parent / 'upstream' / f'AusweisApp-{version}.tar.gz')
if not original.exists():
    raise SystemExit(f'Missing original source archive: {original}')
with original.open('rb') as f:
    digest = hashlib.file_digest(f, 'sha256').hexdigest()
if digest != lock['files'][original.name]['sha256']:
    raise SystemExit(f'SHA256 mismatch: {original}')
shutil.copy2(original, archive)
tree.mkdir()
with tarfile.open(archive) as tf:
    for m in tf:
        parts = pathlib.PurePosixPath(m.name).parts
        if len(parts) < 2:
            continue
        m.name = str(pathlib.PurePosixPath(*parts[1:]))
        tf.extract(m, tree, filter='data')
shutil.copytree(repo / 'debian', tree / 'debian')
changelog = tree / 'debian/changelog'
changelog.write_text(re.sub(r'^ausweisapp \([^\n]+\) \S+;',
                           f'ausweisapp ({package_version(lock, a.series)}) {a.series};',
                           changelog.read_text(), count=1))
if a.series != 'resolute':
    if a.dependencies is None:
        raise SystemExit('--dependencies is required for private Qt builds')
    for name in ['control', 'rules']:
        shutil.copy2(repo / 'packaging/linux/debian-portable' / name, tree / 'debian' / name)
    for name in ['build-private-deps.sh', 'install-notices.py']:
        shutil.copy2(repo / 'packaging/linux' / name, tree / 'debian' / name)
    for component in ['qt', 'llhttp', 'cmake-bootstrap']:
        source = a.dependencies.resolve() / component
        target = tree / component
        shutil.copytree(source, target, symlinks=True)
        # llhttp's configure step writes this generated file into its source tree.
        if component == 'llhttp':
            (target / 'libllhttp.pc').unlink(missing_ok=True)
        component_tar = out / f'ausweisapp_{version}.orig-{component}.tar.xz'
        subprocess.run(['tar', '--sort=name', '--owner=0', '--group=0', '--numeric-owner', f"--mtime=@{lock['source_date_epoch']}", '-cJf', str(component_tar), '-C', str(tree), component], check=True,
                       env={**__import__('os').environ, 'XZ_OPT': '-T4 -3'})
print(tree)
print('Next: dpkg-buildpackage -S -sa -us -uc -d in this tree (offline, unsigned).')
