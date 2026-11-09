"""Konstanten fuer Heliotherm WebMI."""
DOMAIN = "heliotherm_webmi"
CONF_INTERVAL = "interval"
DEFAULT_INTERVAL = 60

# Service-Login des Reglers: fest vorgegeben, nicht aenderbar und oeffentlich bekannt
WEBMI_USER = "admin"
WEBMI_PASSWORD = "superuser"

# Schluessel -> WebMI-Adresse (aus den SVG-Seiten 00000084 / 00000085)
ADDR = {
    "hkp_ist": "webregler/mp/247/value",
    "hkp_hand_aktiv": "webregler/mp/247/handAkt",
    "hkp_handwert": "webregler/mp/247/handVal",
    "eq_ist": "webregler/mp/248/value",
    "eq_hand_aktiv": "webregler/mp/248/handAkt",
    "eq_handwert": "webregler/mp/248/handVal",
}
