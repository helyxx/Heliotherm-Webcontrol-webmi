# Heliotherm WebControl (WebMI) – Home Assistant Integration

Liest ueber die **WebControl-App von Heliotherm** die Pumpenwerte aus und stellt diese auch als Handwert zur Verfuegung.

Custom Integration fuer Home Assistant, die ueber die **WebMI-Schnittstelle** des Heliotherm-WebControl-Reglers
die Umwaelzpumpen ausliest und im Handbetrieb steuert. Sie ergaenzt die Modbus-Integration
[ha_heliotherm](https://github.com/helyxx/ha_heliotherm_PV) um Werte, die nur ueber WebControl erreichbar sind.

## Entitaeten

| Entitaet | Typ | WebMI-Adresse |
|---|---|---|
| HKP Istwert / EQ Istwert | Sensor (%) | `webregler/mp/247/value`, `webregler/mp/248/value` |
| HKP Handbetrieb / EQ Handbetrieb | Switch (aus = Automatik) | `.../handAkt` |
| HKP Handwert / EQ Handwert | Number (0–100 %) | `.../handVal` |

HKP = Heizkreispumpe, EQ = Quellenpumpe.

## Installation

**HACS:** *Custom repository* `https://github.com/helyxx/heliotherm_webmi`, Kategorie *Integration*.

**Manuell:** Ordner `custom_components/heliotherm_webmi` nach `config/custom_components/` kopieren und Home Assistant neu starten.

Danach *Einstellungen → Geraete & Dienste → Integration hinzufuegen → Heliotherm WebControl (WebMI)*,
Host des Reglers und Abfrageintervall (Standard 60 s) eintragen.

## Hinweise

- Lesen funktioniert ohne Login; zum Schreiben meldet sich die Integration mit dem fest im Regler
  hinterlegten Service-Login an (siehe `const.py`).
- Der Login laeuft ueber das WebMI-Verfahren des Reglers (RSA-verschluesseltes Passwort, Session mit MD5-Digest).
- Schreibzugriffe greifen direkt in den Pumpenbetrieb ein – Handbetrieb nach Gebrauch wieder ausschalten.
