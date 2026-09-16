# AusweisApp 2.5.5 für Linux, amd64

Community-Build aus den Quellen von Governikus/AusweisApp, kein offizielles Linux-Release von Governikus.

| System | Datei |
|---|---|
| Ubuntu 22.04 | `ausweisapp_2.5.5-0build1.ubuntu22.04_amd64.deb` |
| Ubuntu 24.04 | `ausweisapp_2.5.5-0build1.ubuntu24.04_amd64.deb` |
| Ubuntu 26.04 | `ausweisapp_2.5.5-0build1.ubuntu26.04_amd64.deb` |
| AppImage, auf allen drei Versionen geprüft | `AusweisApp-2.5.5-x86_64.AppImage` |

## Installation

Lade nur das zum System passende Paket herunter. Beispiel für Ubuntu 24.04:

```bash
sudo apt install ./ausweisapp_2.5.5-0build1.ubuntu24.04_amd64.deb
```

Für das AppImage: Datei nach `~/Applications` kopieren und ausführbar machen. Es benötigt die Grafikbibliotheken des Systems, darunter `libgl1`, `libopengl0` und `libegl1`.

```bash
mkdir -p "$HOME/Applications"
cp AusweisApp-2.5.5-x86_64.AppImage "$HOME/Applications/"
chmod +x "$HOME/Applications/AusweisApp-2.5.5-x86_64.AppImage"
"$HOME/Applications/AusweisApp-2.5.5-x86_64.AppImage"
```

Falls FUSE nicht verfügbar ist, starte mit `--appimage-extract-and-run`.

## AppImage-Symbol in GNOME

Lade auch `integrate-appimage.py` herunter und führe es ohne sudo aus:

```bash
python3 integrate-appimage.py "$HOME/Applications/AusweisApp-2.5.5-x86_64.AppImage"
```

Das Skript registriert die Anwendung im Menü, ordnet ihr das Symbol zu und setzt das Dateisymbol über GIO/GVfs. Starte die Anwendung danach neu und aktualisiere die Dateiansicht. Die sichtbare Darstellung im Dock muss auf dem jeweiligen Desktop geprüft werden. Die Integration erfolgt pro Benutzer und wird nicht allein durch Herunterladen der AppImage-Datei eingerichtet.

Führe das Skript nur mit einem vertrauenswürdigen AppImage aus. Bei einem neuen Dateipfad ist die Integration erneut auszuführen. Sie hat Vorrang vor einem gleichnamigen Desktopeintrag aus einem installierten Debian-Paket. Entfernen:

```bash
python3 integrate-appimage.py "$HOME/Applications/AusweisApp-2.5.5-x86_64.AppImage" --remove
```

## Prüfsummen und Quellen

Bei vollständig heruntergeladenen Release-Dateien: `sha256sum -c SHA256SUMS`. Für einzelne Downloads vergleiche deren `sha256sum DATEI` mit dem entsprechenden Eintrag im Manifest.

Die drei `sources-*.tar` enthalten die vollständigen Debian-Quellpakete je Ubuntu-Version, einschließlich der benötigten externen Quellkomponenten. `AusweisApp-2.5.5-packaging.tar` enthält die lokalen Paketierungsrezepte. Die ursprünglichen Quellpakete und Lizenztexte werden unverändert bereitgestellt. Die automatisch von GitHub erzeugten Quellcodearchive enthalten diese zusätzlichen Komponenten nicht.

Upstream und Release: Tag `2.5.5`, Commit `6724c548f9ab5f50d674960b5e2a736318815089`. Die eigenen Paketierungsquellen stehen auf der Branch `linux-packaging` und zusätzlich im Paketierungsarchiv. Der ursprüngliche Anwendungstag bleibt unverändert.

Debian-Versionierung: `2.5.5-0build1~ubuntuXX.04`, Architektur `amd64`. Die Buildnummer bezeichnet die Paketierungsrevision, nicht eine andere Anwendungsversion. Bei bereits installierten früheren Entwicklungspaketen kann diese Version als Downgrade gelten; das konkrete Paket dann interaktiv mit `sudo apt install ./DATEI.deb` installieren und die angezeigte Änderung prüfen.

Ubuntu 22.04/24.04 und AppImage verwenden privates Qt 6.10.2. Ubuntu 26.04 verwendet Qt 6.10.2 aus der Distribution. Die Paketversionen enthalten weiterhin `0build1`, entsprechend der einheitlichen Paketierungskonvention.

## Prüfung und Grenzen

Die neu versionierten Debian-Pakete wurden erneut in sauberen Containern installiert und gestartet; lintian meldete keine Diagnosen. Das neu erzeugte AppImage wurde auf allen drei Ubuntu-Versionen und in einer virtuellen Wayland-Sitzung geprüft. Die erste Validierung der unveränderten Anwendungsquellen umfasste 513 bestandene Upstream-Tests auf Ubuntu 26.04; diese vollständige Suite wurde für die reine Paketierungsänderung nicht erneut ausgeführt.

Nicht geprüft: echte eID-Authentifizierung mit Ausweis/Kartenleser, FUSE-Mount und GPU-Beschleunigung auf dem Benutzerdesktop. Für USB-Kartenleser können `pcscd` und ein geeigneter Treiber erforderlich sein. Die Quellpakete sind nicht signiert; dieses Release ist keine Launchpad-/PPA-Veröffentlichung.

GitHub normalisiert das Zeichen `~` in Asset-Dateinamen zu `.`. Die interne Debian-Version enthält weiterhin `~`, zum Beispiel `2.5.5-0build1~ubuntu24.04`.
