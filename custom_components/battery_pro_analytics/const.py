"""Constants for the Advanced Battery Analytics integration."""

DOMAIN = "battery_pro_analytics"

# Standardwerte für die Berechnungen
DEFAULT_NOMINAL_CAPACITY = 25.0  # Ah laut Datenblatt
SOH_THRESHOLD_EOL = 80.0         # End of Life Schwelle in %
# Fallback, falls noch nicht genügend Daten für eine eigene Berechnung vorliegen
CONF_FALLBACK_CYCLES_YEAR = 200
# Schwellenwert: Ab wie vielen Tagen Laufzeit vertrauen wir der eigenen Statistik?
MIN_DAYS_FOR_PROGNOSIS = 14

# Scan Intervall (Wie oft sollen die Daten vom Inverter geholt werden?)
# Standardmäßig alle 50 Sekunden
SCAN_INTERVAL_SECONDS = 60

# Keys für das Daten-Dictionary (damit rctclient und sensor die gleiche Sprache sprechen)
ATTR_CELL_DRIFT = "cell_drift"
ATTR_SOH = "state_of_health"
ATTR_REMAINING_CYCLES = "remaining_cycles"
ATTR_REMAINING_YEARS = "remaining_years"
ATTR_CURRENT_CAPACITY = "current_capacity"