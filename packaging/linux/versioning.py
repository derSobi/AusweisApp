#!/usr/bin/env python3
"""Einheitliche Debian-Versionen aus release-lock.json ableiten."""
import argparse
import json
from pathlib import Path
import re

UBUNTU = {"jammy": "22.04", "noble": "24.04", "resolute": "26.04"}


def package_version(lock, series):
    version = lock["upstream_tag"]
    revision = lock["debian_revision"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Ungültige Upstream-Version")
    if not re.fullmatch(r"0build[1-9]\d*", revision):
        raise ValueError("Debian-Revision muss 0buildN mit N >= 1 sein")
    return f"{version}-{revision}~ubuntu{UBUNTU[series]}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("series", choices=UBUNTU, help="Ubuntu-Serie")
    parser.add_argument("--filename", action="store_true", help="Debian-Dateiname mit Architektur")
    args = parser.parse_args()
    lock = json.loads(Path(__file__).with_name("release-lock.json").read_text())
    value = package_version(lock, args.series)
    print(f"ausweisapp_{value}_{lock['architecture']}.deb" if args.filename else value)
