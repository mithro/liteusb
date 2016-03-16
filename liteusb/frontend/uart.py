from litex.gen import *

from liteusb.common import *
from misoclib.com.uart import UART

class LiteUSBUARTPHY:
    def __init__(self):
        self.sink = stream.Endpoint([("data", 8)])
        self.source = stream.Endpoint([("data", 8)])

class LiteUSBUART(UART):
    def __init__(self, port,
                 tx_fifo_depth=16,
                 rx_fifo_depth=16):

        phy = LiteUSBUARTPHY()
        UART.__init__(self, phy, tx_fifo_depth, rx_fifo_depth)

        # TX
        self.comb += [
            port.sink.valid.eq(phy.sink.valid),
            port.sink.last.eq(1),
            port.sink.length.eq(1),
            port.sink.dst.eq(port.tag),
            port.sink.data.eq(phy.sink.data),
            phy.sink.ready.eq(port.sink.ready)
        ]

        # RX
        self.comb += [
            phy.source.valid.eq(port.source.valid),
            phy.source.data.eq(port.source.data),
            port.source.ready.eq(phy.source.ready)
        ]
