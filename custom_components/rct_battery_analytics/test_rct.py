import asyncio
import sys
import os
import socket

# Pfad-Setup
sys.path.append(os.path.dirname(__file__))

async def quick_check():
    host = "192.168.1.3"
    port = 8899
    print(f"--- Hardcore-Check auf {host}:{port} ---")
    
    # Schritt 1: Kann der Port überhaupt geöffnet werden?
    print("1. Teste TCP-Socket Verbindung...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((host, port))
        print("✅ TCP-Verbindung erfolgreich hergestellt!")
    except Exception as e:
        print(f"❌ TCP-Verbindung fehlgeschlagen: {e}")
        print("TIPP: Sind andere Clients aktiv? Bitte mal kurz abschalten!")
        return

    # Schritt 2: Versuche die Logik-Klasse zu nutzen
    print("\n2. Teste rctclient_logic Abfrage...")
    from rctclient_logic import RctDataFetcher
    fetcher = RctDataFetcher(host)
    
    try:
        # Wir fragen NUR den SOC ab für den Test
        result = await fetcher.read_value("battery.soc")
        if result is not None:
            print(f"✅ ERFOLG! SOC ist: {result}%")
        else:
            print("⚠️ Verbindung stand, aber Inverter hat keine Daten gesendet.")
    except Exception as e:
        print(f"❌ Fehler während der Abfrage: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    asyncio.run(quick_check())