from litex.soc.interconnect import stream

from liteusb.common import *
from liteusb.core.packet import LiteUSBPacketizer, LiteUSBDepacketizer
from liteusb.core.crc import LiteUSBCRC32Inserter, LiteUSBCRC32Checker
from liteusb.core.crossbar import LiteUSBCrossbar

class LiteUSBCore(Module):
    def __init__(self, phy, clk_freq, with_crc=True):
        rx_pipeline = [phy]
        tx_pipeline = [phy]

        # depacketizer / packetizer
        self.submodules.depacketizer = LiteUSBDepacketizer(clk_freq)
        self.submodules.packetizer = LiteUSBPacketizer()
        rx_pipeline += [self.depacketizer]
        tx_pipeline += [self.packetizer]

        if with_crc:
            # crc checker / inserter
            self.submodules.crc_rx = LiteUSBCRC32Checker()
            self.submodules.crc_tx = LiteUSBCRC32Inserter()
            rx_pipeline += [self.crc_rx]
            tx_pipeline += [self.crc_tx]

        # crossbar
        self.submodules.crossbar = LiteUSBCrossbar()
        rx_pipeline += [self.crossbar.master]
        tx_pipeline += [self.crossbar.master]

        # graph
        self.submodules.rx_pipeline = stream.Pipeline(*rx_pipeline)
        self.submodules.tx_pipeline = stream.Pipeline(*reversed(tx_pipeline))
