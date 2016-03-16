from litex.gen import *
from litex.gen.genlib.fsm import *

from litex.soc.interconnect import stream
from litex.soc.interconnect.stream import EndpointDescription
from litex.soc.interconnect.stream_packet import *


packet_header_length = 9
packet_header_fields = {
    "preamble": HeaderField(0,  0, 32),
    "dst":      HeaderField(4,  0,  8),
    "length":   HeaderField(5,  0, 32)
}
packet_header = Header(packet_header_fields,
                       packet_header_length,
                       swap_field_bytes=True)


def phy_description(dw):
    payload_layout = [("data", dw)]
    return EndpointDescription(payload_layout)


def packet_description(dw):
    param_layout = packet_header.get_layout()
    payload_layout = [
        ("data", dw),
        ("error", dw//8)
    ]
    return EndpointDescription(payload_layout, param_layout)


def user_description(dw):
    param_layout = [
        ("dst",    8),
        ("length", 32)
    ]
    payload_layout = [
        ("data", dw),
        ("error", dw//8)
    ]
    return EndpointDescription(payload_layout, param_layout)


class LiteUSBMasterPort:
    def __init__(self, dw):
        self.source = stream.Endpoint(user_description(dw))
        self.sink = stream.Endpoint(user_description(dw))


class LiteUSBSlavePort:
    def __init__(self, dw, tag):
        self.sink = stream.Endpoint(user_description(dw))
        self.source = stream.Endpoint(user_description(dw))
        self.tag = tag


class LiteUSBUserPort(LiteUSBSlavePort):
    def __init__(self, dw, tag):
        LiteUSBSlavePort.__init__(self, dw, tag)
