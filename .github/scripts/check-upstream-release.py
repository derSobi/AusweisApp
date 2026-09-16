#!/usr/bin/env python3
"""Neue stabile Upstream-Versionen prüfen und genau ein Issue je Version erstellen."""
import argparse
import base64
import json
import os
import re
import urllib.request

REPOSITORY = 'derSobi/AusweisApp'
UPSTREAM = 'Governikus/AusweisApp'


def api(path, data=None):
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('GitHub-Token fehlt')
    request = urllib.request.Request(
        'https://api.github.com/' + path,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Accept': 'application/vnd.github+json', 'Authorization': f'Bearer {token}',
                 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'AusweisApp-Release-Pruefung'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def version(tag):
    if not re.fullmatch(r'\d+\.\d+\.\d+', tag):
        raise ValueError('Unbekanntes Versionsformat; manuelle Prüfung erforderlich')
    return tuple(map(int, tag.split('.')))


def check(call=api, dry_run=False):
    if os.environ.get('GITHUB_REPOSITORY', REPOSITORY) != REPOSITORY:
        raise RuntimeError('Workflow ist ausschließlich für derSobi/AusweisApp bestimmt')
    content = call(f'repos/{REPOSITORY}/contents/packaging/linux/release-lock.json?ref=linux-packaging')
    lock = json.loads(base64.b64decode(content['content']))
    release = call(f'repos/{UPSTREAM}/releases/latest')
    tag = release['tag_name']
    if release['draft'] or release['prerelease']:
        raise ValueError('Kein stabiles Upstream-Release')
    if version(tag) <= version(lock['upstream_tag']):
        return f"Kein Update: paketiert {lock['upstream_tag']}, Upstream {tag}."
    marker = f'<!-- ausweisapp-upstream-release:{tag} -->'
    page = 1
    while True:
        issues = call(f'repos/{REPOSITORY}/issues?state=all&per_page=100&page={page}')
        for issue in issues:
            if 'pull_request' not in issue and marker in (issue.get('body') or ''):
                return f"Bereits erfasst: {issue['html_url']}"
        if len(issues) < 100:
            break
        page += 1
    title = f'Neue Upstream-Version {tag}: Linux-Pakete aktualisieren'
    body = f'''{marker}
## Neue stabile Version

Upstream: [{tag}](https://github.com/{UPSTREAM}/releases/tag/{tag})
Aktuell paketiert: `{lock['upstream_tag']}`.

Ein automatischer Build ist noch nicht eingerichtet. Die Aktualisierung muss geprüft und gebaut werden.

## Aufgaben

- [ ] Upstream-Tag, Commit und Quellarchiv prüfen.
- [ ] Änderungen und Abhängigkeiten auf `linux-packaging` integrieren.
- [ ] Lockfile und Debian-Changelog aktualisieren; neue Version mit `0build1` beginnen.
- [ ] Pakete für Ubuntu 22.04, 24.04 und 26.04 sowie AppImage bauen.
- [ ] Installation, Tests, lintian und SHA-256 prüfen.
- [ ] Release-Draft mit dem originalen Upstream-Tag vorbereiten und nach Prüfung veröffentlichen.

Dieses Issue wird pro Version nur einmal angelegt, auch wenn es später geschlossen wird.
'''
    if dry_run:
        return f'Testlauf: Issue würde erstellt: {title}'
    issue = call(f'repos/{REPOSITORY}/issues',
                 {'title': title, 'body': body, 'assignees': ['derSobi']})
    return f"Issue erstellt: {issue['html_url']}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Nur prüfen, kein Issue erstellen')
    result = check(dry_run=parser.parse_args().dry_run)
    print(result)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as stream:
            stream.write(result + '\n')
