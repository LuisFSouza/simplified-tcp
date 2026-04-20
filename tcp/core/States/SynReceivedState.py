from .TCPState import TCPState
from .EstablishedState import EstablishedState
import logging

class SynReceivedState(TCPState):
    def on_ack(self, packet, addr):
        header = packet.header
        logging.warning("ACK recebido em SYN-RECEIVED")
        if header.ack_number == self.context.seq_number:
            with self.context.lock:
                self.context.send_buffer.clear()
                self.context.send_base = header.ack_number
            self.transition(EstablishedState)
        else:
            logging.warning("ACK invalido no SYN-RECEIVED, ignorando.")

