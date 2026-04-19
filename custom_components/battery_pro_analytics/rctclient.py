import logging
from rctclient.registry import REGISTRY
from rctclient.transport import RequestHandler

_LOGGER = logging.getLogger(__name__)

class RctDataFetcher:
    """Class to handle communication with the RCT Power Inverter."""

    def __init__(self, host):
        self.host = host
        self.port = 8899
        self.module_map = {}

    def get_rct_value(self, name):
        """
        Native Python implementation of a single value read.
        Bypasses the CLI and uses the library's RequestHandler directly.
        """
        try:
            handler = RequestHandler(self.host, self.port)
            # Get object definition from the built-in registry
            object_info = REGISTRY.get_by_name(name)
            
            # Execute the read request
            response = handler.read(object_info)
            
            if response and hasattr(response, "value"):
                return response.value
            return None
            
        except Exception as err:
            _LOGGER.debug("Error reading %s from RCT: %s", name, err)
            return None

    def fetch_module_sns(self):
        """Once-per-session fetch of module serial numbers to identify stacks."""
        self.module_map = {}
        for i in range(7):
            sn = self.get_rct_value(f"battery.module_sn[{i}]")
            # Filter out empty or zeroed serial numbers
            if sn and str(sn).strip() not in ["0", "None", ""]:
                clean_sn = str(sn).replace(" ", "")
                self.module_map[i] = clean_sn
        
        _LOGGER.info("Detected %s battery modules via RCT registry", len(self.module_map))
        return self.module_map

    def fetch_all_data(self):
        """
        The main data collection method called by the DataUpdateCoordinator.
        Collects all metrics required for the 'Advanced Battery Analytics' sensors.
        """
        data = {}

        # 1. Base Battery Metrics
        data["ah_capacity"] = self.get_rct_value("battery.ah_capacity")
        data["min_cell_v"] = self.get_rct_value("battery.min_cell_voltage")
        data["max_cell_v"] = self.get_rct_value("battery.max_cell_voltage")
        data["soc"] = self.get_rct_value("battery.soc")
        data["soh_internal"] = self.get_rct_value("battery.soh") # Manufacturer's SOH

        # 2. Module Level Data & Senior Detection
        if not self.module_map:
            self.fetch_module_sns()

        module_data = {}
        max_cycles = 0
        
        for idx, sn in self.module_map.items():
            cycles = self.get_rct_value(f"battery.stack_cycles[{idx}]")
            voltage = self.get_