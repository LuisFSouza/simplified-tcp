import logging
from ctypes import c_uint16
from .TCPState import TCPState
from .TimeWaitState import TimeWaitState

class ClosingState(TCPState):
    def on_ack(self, packet, addr):
        header = packet.header
        if header.ack_number == self.context.seq_number:
            logging.warning("ACK do FIN recebido em CLOSING. Indo para TIME_WAIT...")
            self.transition(TimeWaitState)
        else:
            logging.info("ACK recebido em CLOSING. Ignorando...")

    def on_fin(self, packet, addr):
        header = packet.header
        logging.warning("FIN duplicado em CLOSING. Reenviando ACK...")
        self.context.ack_number = c_uint16(header.seq_number + 1).value
        self.context.send_ack()
