from .TCPState import TCPState
from .SynReceivedState import SynReceivedState
import random
from ctypes import c_uint16

class ListenState(TCPState):
    def on_syn(self, packet, addr):
        header = packet.header
        self.context.remote_addr = addr
        self.context.ack_number = c_uint16(header.seq_number + 1).value
        self.context.seq_number = random.randint(0, 65535)
        self.context.send_base = self.context.seq_number
        syn_ack = self.context.send_syn_ack()
        self.context.buffer_packet(syn_ack)
        self.transition(SynReceivedState)