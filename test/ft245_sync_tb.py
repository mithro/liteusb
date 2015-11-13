from migen import *
from migen.fhdl.specials import Tristate

from liteusb.common import *
from liteusb.phy.ft245 import FT245PHYSynchronous

from test.common import *

class RandRun:
    def __init__(self, level=0):
        self.run = True
        self.level = level

    def do_simulation(self):
        self.run = True
        n = randn(100)
        if n < self.level:
            self.run = False

class FT245SynchronousModel(Module, RandRun):
    def __init__(self, rd_data):
        RandRun.__init__(self, 10)
        self.rd_data = [0] + rd_data
        self.rd_idx = 0

        # pads
        self.data = Signal(8)
        self.rxf_n = Signal(reset=1)
        self.txe_n = Signal(reset=1)
        self.rd_n = Signal(reset=1)
        self.wr_n = Signal(reset=1)
        self.oe_n = Signal(reset=1)
        self.siwua = Signal()
        self.pwren_n = Signal(reset=1)

        self.wr_data = []
        self.wait_wr_n = False
        self.rd_done = 0


        self.data_w = Signal(8)
        self.data_r = Signal(8)

        #self.specials += Tristate(self.data, self.data_r, ~self.oe_n, self.data_w)

    def tristate_sim(self):
        if (yield self.oe_n):
            yield self.data_r.eq(self.data)
        yield self.data_w.eq(self.data)

    def wr_sim(self):
        print("wr_sim")
        if not (yield self.wr_n) and not (yield self.txe_n):
            self.wr_data.append((yield self.data_w))
            self.wait_wr_n = False

        if not self.wait_wr_n:
            if self.run:
                yield self.txe_n.eq(1)
            else:
                if (yield self.txe_n):
                    self.wait_wr_n = True
                yield self.txe_n.eq(0)

    def rd_sim(self):
        print("rd_sim")
        rxf_n = (yield self.rxf_n)
        if self.run:
            if self.rd_idx < len(self.rd_data)-1:
                self.rd_done = (yield self.rxf_n)
                yield self.rxf_n.eq(0)
            else:
                yield self.rxf_n.eq(self.rd_done)
        else:
            yield self.rxf_n.eq(self.rd_done)

        if not (yield self.rd_n) and not (yield self.oe_n):
            if self.rd_idx < len(self.rd_data)-1:
                self.rd_idx += not rxf_n
            yield self.data_r.eq(self.rd_data[self.rd_idx])
            self.rd_done = 1

    def generator(self):
        yield self.rxf_n.eq(0)
        self.wr_data = []
        while True:
            RandRun.do_simulation(self)
            yield from self.tristate_sim()
            yield from self.wr_sim()
            yield from self.rd_sim()
            yield

test_packet = [i%256 for i in range(512)]


class TB(Module):
    def __init__(self):
        self.submodules.model = FT245SynchronousModel(test_packet)
        self.submodules.phy = FT245PHYSynchronous(self.model, 100*1e6)

        self.submodules.streamer = PacketStreamer(phy_description(8))
        self.submodules.streamer_randomizer = AckRandomizer(phy_description(8), level=10)

        self.submodules.logger_randomizer = AckRandomizer(phy_description(8), level=10)
        self.submodules.logger = PacketLogger(phy_description(8))

        self.comb += [
            Record.connect(self.streamer.source, self.streamer_randomizer.sink),
            self.phy.sink.stb.eq(self.streamer_randomizer.source.stb),
            self.phy.sink.data.eq(self.streamer_randomizer.source.data),
            self.streamer_randomizer.source.ack.eq(self.phy.sink.ack),

            self.logger_randomizer.sink.stb.eq(self.phy.source.stb),
            self.logger_randomizer.sink.data.eq(self.phy.source.data),
            self.phy.source.ack.eq(self.logger_randomizer.sink.ack),
            Record.connect(self.logger_randomizer.source, self.logger.sink)
        ]


def main_generator(dut):
    dut.streamer.send(Packet(test_packet))
    for i in range(256):
        print(len(dut.streamer.packet))
        yield
    #s, l, e = check(test_packet, dut.model.wr_data)
    #print("shift " + str(s) + " / length " + str(l) + " / errors " + str(e))

    #s, l, e = check(test_packet, dut.logger.packet[1:])
    #print("shift " + str(s) + " / length " + str(l) + " / errors " + str(e))

    # XXX: find a way to exit properly
    import sys
    sys.exit()


if __name__ == "__main__":
    tb = TB()
    generators = {
        "sys" :   [main_generator(tb),
                   tb.streamer.generator(),
                   tb.streamer_randomizer.generator(),
                   tb.logger_randomizer.generator(),
                   tb.logger.generator()],
        "usb":    tb.model.generator()
    }
    clocks = {"sys": 10,
              "usb": 10}
    run_simulation(tb, generators, clocks, vcd_name="sim.vcd")
