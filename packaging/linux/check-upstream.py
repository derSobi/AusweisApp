#!/usr/bin/env python3
"""Read the latest stable upstream release without changing Git or publishing."""
import json
import re
from pathlib import Path
import urllib.request
lock = json.loads(Path(__file__).with_name('release-lock.json').read_text())
request = urllib.request.Request(
    'https://api.github.com/repos/Governikus/AusweisApp/releases/latest',
    headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'AusweisApp-local-build'})
with urllib.request.urlopen(request, timeout=30) as response:
    release = json.load(response)
tag = release['tag_name']
if release['draft'] or release['prerelease'] or not re.fullmatch(r'\d+\.\d+\.\d+', tag):
    raise SystemExit('Unexpected release metadata; manual inspection required')
print(json.dumps({'packaged': lock['upstream_tag'], 'latest_stable_release': tag,
                  'published_at': release['published_at'], 'url': release['html_url'],
                  'update_available': tuple(map(int, tag.split('.'))) > tuple(map(int, lock['upstream_tag'].split('.'))),
                  'publication_enabled': False}, indent=2))
