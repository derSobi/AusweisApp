#!/usr/bin/env python3
"""Ein vertrauenswürdiges AusweisApp-AppImage für den aktuellen Benutzer einrichten."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

APP_ID = "com.governikus.ausweisapp2"
MARKER = "X-AusweisApp-Integration=true"


def desktop_string(value):
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def exec_argument(value):
    # Exec quoting is parsed after the desktop entry string escape layer.
    escaped = value.replace("%", "%%")
    for char in ('\\', '"', '`', '$'):
        escaped = escaped.replace(char, "\\" + char)
    return desktop_string('"' + escaped + '"')


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False, usage="%(prog)s [-h] [--remove] [--no-file-icon] APPIMAGE")
    parser.add_argument("-h", "--help", action="help", help="Diese Hilfe anzeigen und beenden")
    parser._positionals.title = "Positionsargumente"
    parser._optionals.title = "Optionen"
    parser.add_argument("appimage", type=Path, help="Vertrauenswürdiges AppImage am dauerhaften Speicherort")
    parser.add_argument("--remove", action="store_true", help="Desktopeintrag und Symbol dieses Skripts entfernen")
    parser.add_argument("--no-file-icon", action="store_true", help="GNOME/GVfs-Dateimetadaten überspringen")
    args = parser.parse_args()
    appimage = args.appimage.expanduser().resolve()
    data = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    if not data.is_absolute():
        parser.error("XDG_DATA_HOME muss ein absoluter Pfad sein")
    desktop = data / "applications" / (APP_ID + ".desktop")
    icon = data / "icons/hicolor/scalable/apps/ausweisapp-appimage.svg"
    if desktop.is_symlink() or (desktop.exists() and MARKER not in desktop.read_text()):
        parser.error(f"Ein fremder Desktopeintrag wird nicht ersetzt: {desktop}")
    if args.remove:
        if not desktop.exists():
            parser.error("Kein verwalteter Desktopeintrag zum Entfernen vorhanden")
        desktop.unlink()
        icon.unlink(missing_ok=True)
    else:
        if not appimage.is_file() or not os.access(appimage, os.X_OK):
            parser.error("Das AppImage muss vorhanden und ausführbar sein")
        # Only run this for a trusted image: --appimage-extract executes its runtime.
        with tempfile.TemporaryDirectory(prefix="ausweisapp-icon-") as temporary:
            member = "usr/share/icons/hicolor/scalable/apps/AusweisApp.svg"
            subprocess.run([str(appimage), "--appimage-extract", member], cwd=temporary,
                           check=True, stdout=subprocess.DEVNULL)
            extracted = Path(temporary) / "squashfs-root" / member
            if not extracted.is_file():
                parser.error("Das AusweisApp-Symbol wurde im AppImage nicht gefunden")
            icon.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(extracted, icon)
        desktop.parent.mkdir(parents=True, exist_ok=True)
        desktop.write_text(
            "[Desktop Entry]\nType=Application\nName=AusweisApp (AppImage)\n"
            # A fixed executable also avoids GLib probing a literal %% path
            # before the desktop field codes have been expanded.
            f"Exec=/usr/bin/env {exec_argument(str(appimage))}\n"
            f"Icon={desktop_string(str(icon))}\n"
            "Terminal=false\nStartupNotify=true\nStartupWMClass=AusweisApp\n"
            "Categories=System;Security;\nKeywords=eID;Ausweis;Identity;\n"
            f"{MARKER}\n", encoding="utf-8")
        desktop.chmod(0o644)
    if shutil.which("update-desktop-database"):
        subprocess.run(["update-desktop-database", str(desktop.parent)], check=True)
    if not args.no_file_icon:
        if not shutil.which("gio"):
            print("WARNUNG: gio fehlt; das Dateisymbol wurde nicht geändert.")
        else:
            if args.remove:
                current = subprocess.run(
                    ["gio", "info", "-a", "metadata::custom-icon", str(appimage)],
                    check=False, capture_output=True, text=True)
                if f"metadata::custom-icon: {icon.as_uri()}" not in current.stdout:
                    print("Desktopintegration entfernt; fremde Dateimetadaten wurden beibehalten.")
                    return
                command = ["gio", "set", "-t", "unset", str(appimage), "metadata::custom-icon"]
            else:
                command = ["gio", "set", str(appimage), "metadata::custom-icon", icon.as_uri()]
            result = subprocess.run(command, check=False, capture_output=True, text=True)
            if result.returncode:
                print("WARNUNG: Dateisymbol nicht geändert; bitte in der GNOME-Sitzung ausführen: "
                      + result.stderr.strip())
    print(("Entfernt: " if args.remove else "Installiert: ") + str(desktop))


if __name__ == "__main__":
    main()
