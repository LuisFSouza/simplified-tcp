import logging
from .EstablishedState import EstablishedState
from .TCPState import TCPState
from ctypes import c_uint16

class SynSentState(TCPState):
    def on_syn_ack(self, packet, addr, event):
        logging.warning("Handshake: SYN-ACK recebido")

        received_ack = event.ack_number
        if received_ack != self.context.seq_number:
            logging.warning("ACK inesperado no SYN-ACK, ignorando.")
            return

        self.context.ack_number = c_uint16(event.seq_number + 1).value

        with self.context.lock:
            self.context.pop_first_buffered(
                lambda pkt: pkt.header.syn_flag == 1
            )
            self.context.send_base = received_ack

        self.context.send_ack()
        logging.warning("Transição para estado ESTABLISHED.")
        self.transition(EstablishedState)

