# Home Assistant: Advanced Battery Analytics (RCT Power)

Eine spezialisierte Home Assistant Integration zur tiefergehenden Analyse und Lebensdauer-Prognose für **RCT Power** Batteriespeicher. 

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## 🔋 Über dieses Projekt

Während Standard-Integrationen oft nur Momentanwerte liefern, fokussiert sich **Advanced Battery Analytics** auf den "Gesundheitszustand" (Health) und die langfristige Alterung deines Speichers. Durch den direkten Zugriff auf die RCT-Register via `rctclient` werden präzise Daten für die Kapazitätsberechnung und Zell-Drift-Analyse extrahiert.

### Kernfunktionen
* **SOH-Monitoring:** Berechnung der realen Kapazität in Ah.
* **Aging-Prognose:** Schätzung der Restlebensdauer basierend auf realen Zyklen (einstellbar, Standard: 150 Zyklen/Jahr).
* **Cell Health:** Überwachung des Spannungs-Drifts zwischen den Zellen in Millivolt-Präzision.
* **Smart-Polling:** Verwendet eine stabilisierte Socket-Logik (basierend auf der RCT-CLI), um Verbindungsabbrüche und Blockaden des Wechselrichters zu minimieren.

---

## 🛠 Installation

1.  Kopiere den Ordner `battery_pro_analytics` in dein `custom_components` Verzeichnis deiner Home Assistant Installation.
2.  Stelle sicher, dass die `rctlib` (inkl. `rctclient`) im Unterordner vorhanden ist.
3.  Starte Home Assistant neu.
4.  Füge die Integration über **Einstellungen -> Geräte & Dienste -> Integration hinzufügen** hinzu.
5.  Gib die IP-Adresse deines RCT-Wechselrichters ein.

---

## ⚙️ Technische Details

Die Integration nutzt eine spezialisierte Kommunikationsebene, um die Eigenheiten des RCT-Wechselrichters zu berücksichtigen:

* **Sequenzielles Polling:** Werte werden nacheinander abgefragt, um den internen Bus des Inverters nicht zu überlasten.
* **Automatic Disconnect:** Die TCP-Verbindung wird nach jedem Abruf-Intervall sofort geschlossen. Dies stellt sicher, dass andere Clients (wie die RCT Power App oder externe Monitoring-Skripte) weiterhin Zugriff haben.
* **Asynchroner Executor:** Zeitintensive Netzwerkoperationen werden aus dem Haupt-Thread von Home Assistant ausgelagert, um die Performance des Dashboards nicht zu beeinträchtigen.

---

## 📜 Lizenz

Dieses Projekt ist unter der **GPL-3.0-only** lizenziert. Dies ist notwendig, da die zugrunde liegende Kommunikation auf der Arbeit von Peter Oberhofer und Stefan Valouch (`rctclient`) basiert.

Weitere Informationen findest du in der mitgelieferten `LICENSE` Datei.

---

## ⚠️ Disclaimer

Dieses Tool ist eine Privatentwicklung und steht in keiner Verbindung zur RCT Power GmbH. Die Nutzung erfolgt auf eigene Gefahr. Die Berechnungen zur Alterung sind Schätzwerte auf Basis der bereitgestellten Daten.