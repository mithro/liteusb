from migen.genlib.io import CRG

from litex.soc.interconnect.stream import SyncFIFO
from litex.soc.integration.soc_core import SoCCore
from litex.soc.cores.gpio import GPIOOut

from liteusb.common import *
from liteusb.phy.ft245 import FT245PHY
from liteusb.core import LiteUSBCore
from liteusb.frontend.wishbone import LiteUSBWishboneBridge


class LiteUSBSoC(SoCCore):
    csr_map = {}
    csr_map.update(SoCCore.csr_map)

    usb_map = {
        "bridge": 0
    }

    def __init__(self, platform):
        clk_freq = int((1/(platform.default_clk_period))*1000000000)
        SoCCore.__init__(self, platform, clk_freq,
            cpu_type=None,
            csr_data_width=32,
            with_uart=False,
            ident="LiteUSB example design",
            with_timer=False
        )
        self.submodules.crg = CRG(platform.request(platform.default_clk_name))

        self.submodules.usb_phy = FT245PHY(platform.request("usb_fifo"), self.clk_freq)
        self.submodules.usb_core = LiteUSBCore(self.usb_phy, self.clk_freq, with_crc=False)


        # Wishbone Bridge
        usb_bridge_port = self.usb_core.crossbar.get_port(self.usb_map["bridge"])
        self.add_cpu_or_bridge(LiteUSBWishboneBridge(usb_bridge_port, self.clk_freq))
        self.add_wb_master(self.cpu_or_bridge.wishbone)

        # Leds
        leds = Cat(iter([platform.request("user_led", i) for i in range(8)]))
        self.submodules.leds = GPIOOut(leds)

default_subtarget = LiteUSBSoC
