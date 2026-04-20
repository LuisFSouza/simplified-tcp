import logging
from .EstablishedState import EstablishedState
from .TCPState import TCPState
from ctypes import c_uint16

class SynSentState(TCPState):
    def on_syn_ack(self, packet, addr):
        header = packet.header
        logging.warning("Handshake: SYN-ACK recebido")

        received_ack = header.ack_number
        if received_ack != self.context.seq_number:
            logging.warning("ACK inesperado no SYN-ACK, ignorando.")
            return

        self.context.ack_number = c_uint16(header.seq_number + 1).value
        
        syn_seq = self.context.send_base
        with self.context.lock:
            self.context.pop_first_buffered(lambda pkt: pkt.header.syn_flag == 1 and pkt.header.seq_number == syn_seq)
            self.context.send_base = received_ack

        self.context.send_ack()
        self.transition(EstablishedState)
