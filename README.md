# Screen Grab

Eine kleine Windows-Desktop-App zum Aufnehmen und direkten Hochladen von Screenshots zu [ImgBB](https://imgbb.com/). Zusätzlich können vorhandene Bilddateien hochgeladen werden. Nach dem Upload wird der Link automatisch in der Verlaufsliste angezeigt und kann mit einem Klick kopiert und geöffnet werden.

## Funktionen

- Vollbildaufnahme über alle angeschlossenen Monitore
- Upload von PNG-, JPG-, JPEG-, BMP-, GIF- und WEBP-Dateien
- Nicht blockierende Uploads: Die Oberfläche bleibt während des Uploads bedienbar
- Fortschrittsanzeige und verständliche Fehlermeldungen
- Klickbarer Upload-Verlauf mit automatischem Kopieren des Links
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

## Sicherheit

API-Keys gehören nicht in den Quellcode und nicht in Commits. Wenn ein Key versehentlich veröffentlicht wurde, sollte er bei ImgBB sofort erneuert werden.

## Lizenz

Für dieses Projekt ist derzeit keine separate Lizenz hinterlegt.
