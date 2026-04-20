import logging
import socket
import select
import asyncio

# Wir versuchen beide Wege (mit Punkt für HA, ohne für das Testskript)
try:
    try:
        from .rctlib.rctclient.frame import ReceiveFrame, make_frame
        from .rctlib.rctclient.registry import REGISTRY
        from .rctlib.rctclient.types import Command
        from .rctlib.rctclient.utils import decode_value
    except ImportError:
        from rctlib.rctclient.frame import ReceiveFrame, make_frame
        from rctlib.rctclient.registry import REGISTRY
        from rctlib.rctclient.types import Command
        from rctlib.rctclient.utils import decode_value
except ImportError as e:
    logging.error(f"Kritischer Import-Fehler: {e}")

_LOGGER = logging.getLogger(__name__)

class RctDataFetcher:
    def __init__(self, host):
        self.host = host
        self.port = 8899

    def _receive_frame(self, sock, timeout=2):
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
                    break
            else:
                raise TimeoutError("Inverter antwortet nicht")
        return None

    def _sync_read(self, name):
        try:
            # Hier nutzen wir REGISTRY statt R
            oinfo = REGISTRY.get_by_name(name)
        except KeyError:
            _LOGGER.error(f"Name {name} nicht gefunden")
            return None

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        try:
            sock.connect((self.host, self.port))
            # Command.READ und oinfo.object_id wie in der CLI
            request = make_frame(command=Command.READ, id=oinfo.object_id)
            sock.send(request)
            
            rframe = self._receive_frame(sock)
            if rframe and rframe.id == oinfo.object_id:
                return decode_value(oinfo.response_data_type, rframe.data)
        except Exception as e:
            _LOGGER.debug(f"Detail-Fehler bei {name}: {e}")
            return None
        finally:
            sock.close()
        return None

    async def read_value(self, name):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_read, name)

    async def fetch_all_data(self):
        soc = await self.read_value("battery.soc")
        ah = await self.read_value("battery.ah_capacity")
        min_v = await self.read_value("battery.min_cell_voltage")
        max_v = await self.read_value("battery.max_cell_voltage")
        soh = await self.read_value("battery.soh") # Neu hinzugefügt
        
        drift = round(max_v - min_v, 4) if (max_v and min_v) else 0

        return {
            "soc": soc,
            "ah_capacity": ah,
            "min_cell_v": min_v,
            "max_cell_v": max_v,
            "cell_drift": drift,
            "soh": soh
        }