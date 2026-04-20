import logging
import socket
import select
from .rctlib.rctclient.frame import ReceiveFrame, make_frame
from .rctlib.rctclient.registry import REGISTRY as R
from .rctlib.rctclient.types import Command

_LOGGER = logging.getLogger(__name__)

class RctDataFetcher:
    def __init__(self, host):
        self.host = host
        self.port = 8899

    def _receive_frame(self, sock, timeout=2):
        """Original-Logik aus der svalouch CLI zum Empfangen von Frames."""
        frame = ReceiveFrame()
        while True:
            ready_read, _, _ = select.select([sock], [], [], timeout)
            if ready_read:
                buf = sock.recv(1024)
                if len(buf) > 0:
                    i = frame.consume(buf)
                    if frame.complete():
                        return frame
                else:
                    break # Socket geschlossen
            else:
                raise TimeoutError("Inverter hat nicht rechtzeitig geantwortet.")
        return None

    async def read_value(self, name):
        """Führt einen Read-Befehl aus, exakt wie 'rctclient read-value'."""
        try:
            oinfo = R.get_by_name(name)
        except KeyError:
            _LOGGER.error(f"Name {name} nicht in Registry gefunden")
            return None

        # Wir nutzen hier einen synchronen Socket in einem Executor, 
        # um den HA-Event-Loop nicht zu blockieren, aber die stabile CLI-Logik zu nutzen.
        def _exchange():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            try:
                sock.connect((self.host, self.port))
                
                # Den Read-Frame bauen (genau wie in der CLI)
                # Command.READ ist meistens 0x01
                request = make_frame(command=Command.READ, id=oinfo.object_id)
                sock.send(request)
                
                rframe = self._receive_frame(sock)
                
                if rframe and rframe.id == oinfo.object_id:
                    # Wir brauchen hier noch utils für decode_value, falls verfügbar
                    # Oder wir nehmen die einfache Variante:
                    from .rctlib.rctclient.utils import decode_value
                    return decode_value(oinfo.response_data_type, rframe.data)
                
                return None
            except Exception as e:
                _LOGGER.debug(f"Fehler bei Abfrage {name}: {e}")
                return None
            finally:
                sock.close()

        # In Home Assistant führen wir blockierende Socket-Aufrufe so aus:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _exchange)

    async def fetch_all_data(self):
        """Sammelt alle Daten nacheinander."""
        # Wir fragen die Werte nacheinander ab, um den Inverter nicht zu stressen
        soc = await self.read_value("battery.soc")
        ah = await self.read_value("battery.ah_capacity")
        min_v = await self.read_value("battery.min_cell_voltage")
        max_v = await self.read_value("battery.max_cell_voltage")
        
        # Zyklen (meistens 2 Stacks vorhanden)
        c0 = await self.read_value("battery.stack_cycles[0]")
        c1 = await self.read_value("battery.stack_cycles[1]")
        
        cycles = [v for v in [c0, c1] if v is not None]

        return {
            "soc": soc,
            "ah_capacity": ah,
            "min_cell_v": min_v,
            "max_cell_v": max_v,
            "max_cycles_senior": max(cycles) if cycles else 0,
            "cell_drift": round(max_v - min_v, 4) if (max_v and min_v) else 0
        }