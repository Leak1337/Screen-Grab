<h1 align="center">◈ Screen Grab</h1>

<p align="center">
  <strong>Capture. Upload. Share.</strong><br>
  Screenshots in Sekunden vom Bildschirm zum fertigen Share-Link.
</p>

<p align="center">
  <a href="https://github.com/repository-owner/Screen-Grab">
    <img src="https://img.shields.io/badge/status-active-00F5A0?style=for-the-badge" alt="Status: active">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
</p>

Screen Grab ist eine fokussierte Windows-Desktop-App zum Aufnehmen und direkten Hochladen von Screenshots zu [ImgBB](https://imgbb.com/). Die Oberfläche ist auf schnelles Arbeiten ausgelegt: Shortcut drücken, Aufnahme machen, Link kopieren.

## Funktionen

- Vollbildaufnahme über alle angeschlossenen Monitore
- Upload von PNG-, JPG-, JPEG-, BMP-, GIF- und WEBP-Dateien
- Nicht blockierende Uploads: Die Oberfläche bleibt während des Uploads bedienbar
- Fortschrittsanzeige und verständliche Fehlermeldungen
- Klickbarer Upload-Verlauf mit automatischem Kopieren des Links
- Persistenter Verlauf mit Copy- und Open-Aktionen
- Globaler App-Shortcut Ctrl + Shift + S
- Neon-inspirierte Dark-UI mit API-Key-Status und Upload-Feedback
- Temporäre Screenshot-Dateien werden nach dem Upload automatisch entfernt
- API-Key bleibt außerhalb des Quellcodes

## Voraussetzungen

- Windows
- Python 3.10 oder neuer
- Ein ImgBB-API-Key

## Installation

Repository klonen und in den Projektordner wechseln:

~~~powershell
git clone https://github.com/repository-owner/Screen-Grab.git
cd Screen-Grab
~~~

Abhängigkeiten installieren:

~~~powershell
python -m pip install -r requirements.txt
~~~

## API-Key konfigurieren

Der API-Key wird aus der Umgebungsvariable `IMGBB_API_KEY` gelesen und nicht im Repository gespeichert.

Für die aktuelle PowerShell-Sitzung:

~~~powershell
$env:IMGBB_API_KEY = "DEIN_IMGBB_API_KEY"
~~~

Alternativ dauerhaft für den aktuellen Windows-Benutzer:

~~~powershell
[Environment]::SetEnvironmentVariable(
    "IMGBB_API_KEY",
    "DEIN_IMGBB_API_KEY",
    "User"
)
~~~

Nach einer dauerhaften Änderung muss das Terminal neu geöffnet werden.

## Anwendung starten

~~~powershell
python screenshot_uploader_gui.py
~~~

Danach kann ein Screenshot aufgenommen oder eine lokale Bilddatei ausgewählt werden. Der erzeugte Link erscheint anschließend im Bereich `HISTORY`.

## Shortcuts

| Shortcut | Aktion |
| --- | --- |
| Ctrl + Shift + S | Vollbild aufnehmen und hochladen |

## Ablauf

~~~text
Shortcut oder Button
        ↓
Vollbildaufnahme / lokale Datei
        ↓
Upload zu ImgBB
        ↓
Link in Zwischenablage + Verlauf
~~~

## Fehlerbehebung

### `Kein ImgBB API-Key gefunden`

Die Umgebungsvariable ist nicht gesetzt oder das Terminal wurde nach der Konfiguration nicht neu gestartet. Prüfe sie mit:

~~~powershell
if ($env:IMGBB_API_KEY) { "API-Key ist gesetzt" } else { "API-Key fehlt" }
~~~

### Upload schlägt fehl

Prüfe die Internetverbindung und ob der ImgBB-API-Key gültig ist. Die Anwendung verwendet für jede Anfrage ein 30-Sekunden-Timeout.

### Screenshot kann nicht erstellt werden

Stelle sicher, dass Python Zugriff auf die Bildschirme hat und die Anwendung nicht durch eine Sicherheitssoftware blockiert wird.

## Projektstruktur

~~~text
Screen-Grab/
├── screenshot_uploader_gui.py  # Anwendung
├── requirements.txt            # Python-Abhängigkeiten
├── .gitignore                  # Lokale und temporäre Dateien
└── README.md                   # Projektdokumentation
~~~

Der Upload-Verlauf wird lokal unter %APPDATA%\ScreenGrab\history.json gespeichert und verlässt den Rechner nicht.

## Sicherheit

API-Keys gehören nicht in den Quellcode und nicht in Commits. Wenn ein Key versehentlich veröffentlicht wurde, sollte er bei ImgBB sofort erneuert werden.

## Lizenz

Für dieses Projekt ist derzeit keine separate Lizenz hinterlegt.
