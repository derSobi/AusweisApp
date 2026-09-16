#!/usr/bin/env python3
"""Öffentliche Release-Dateien ausschließlich aus einer Positivliste vorbereiten."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
from versioning import UBUNTU, package_version


def stage(artifacts, output):
    repo = Path(__file__).resolve().parents[2]
    lock = json.loads((repo / 'packaging/linux/release-lock.json').read_text())
    version = lock['upstream_tag']
    package_version(lock, 'resolute')  # Validate before constructing paths.
    if lock['architecture'] != 'amd64':
        raise ValueError('Nur amd64 wird unterstützt')
    output.mkdir(parents=True, exist_ok=False)
    for series in UBUNTU:
        name = f"ausweisapp_{package_version(lock, series)}_amd64.deb"
        shutil.copy2(artifacts / 'deb' / name, output / name.replace('~', '.'))
        source = artifacts / 'source' / series
        prefix = f'ausweisapp_{package_version(lock, series)}'
        names = [prefix + suffix for suffix in ('.dsc', '.debian.tar.xz', '_source.changes', '_source.buildinfo')]
        names += [f'ausweisapp_{version}.orig.tar.gz']
        if series != 'resolute':
            names += [f'ausweisapp_{version}.orig-{component}.tar.xz' for component in ('qt', 'llhttp', 'cmake-bootstrap')]
        with tarfile.open(output / f'AusweisApp-{version}-sources-{series}.tar', 'w') as archive:
            for name in names:
                archive.add(source / name, arcname=f'{series}/{name}', recursive=False)
    shutil.copy2(artifacts / 'appimage' / f'AusweisApp-{version}-x86_64.AppImage', output)
    shutil.copy2(repo / 'packaging/linux/integrate-appimage.py', output)
    shutil.copy2(repo / f'packaging/linux/RELEASE-NOTES-{version}.md', output / 'HINWEISE.md')
    # Only committed package recipes, never the whole repository or workspace.
    with (output / f'AusweisApp-{version}-packaging.tar').open('wb') as stream:
        subprocess.run(['git', '-C', str(repo), 'archive', '--format=tar',
                        '--prefix=AusweisApp-linux-packaging/', 'HEAD',
                        'debian', 'packaging/linux'], stdout=stream, check=True)
    for path in output.glob('*.tar'):
        with tarfile.open(path) as archive:
            if any(Path(m.name).name in {'LINUX-BUILD.md', 'BUILD-INFO.json'} for m in archive):
                raise ValueError('Private Datei im Archiv gefunden')
    with (output / 'SHA256SUMS').open('w') as manifest:
        for path in sorted(output.iterdir()):
            if path.name == 'SHA256SUMS':
                continue
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            manifest.write(f'{digest}  {path.name}\n')
    print(f'Öffentliche Release-Dateien vorbereitet: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts', type=Path, help='Verzeichnis der geprüften Artefakte')
    parser.add_argument('output', type=Path, help='Neues, noch nicht vorhandenes Upload-Verzeichnis')
    args = parser.parse_args()
    stage(args.artifacts.resolve(), args.output.resolve())
