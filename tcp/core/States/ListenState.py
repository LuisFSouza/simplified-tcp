from .TCPState import TCPState
from .SynReceivedState import SynReceivedState
import random
from ctypes import c_uint16
import logging

class ListenState(TCPState):
    def on_syn(self, packet, addr, event):
        self.context.remote_addr = addr
        self.context.ack_number = c_uint16(event.seq_number + 1).value
        self.context.seq_number = random.randint(0, 65535)
        self.context.send_base = self.context.seq_number
        syn_ack = self.context.send_packet(syn_flag=1, ack_flag=1)
        self.context.buffer_packet(syn_ack)
        logging.warning("Transição para estado SYN-RECEIVED")
        self.transition(SynReceivedState)