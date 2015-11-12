from migen import *

from liteusb.common import *

from litex.soc.interconnect.wishbonebridge import WishboneStreamingBridge

class LiteUSBWishboneBridge(WishboneStreamingBridge):
    def __init__(self, port, clk_freq):
        WishboneStreamingBridge.__init__(self, port, clk_freq)
        self.comb += port.sink.dst.eq(port.tag)
