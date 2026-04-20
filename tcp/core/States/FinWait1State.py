import logging
from ctypes import c_uint16
from .EstablishedState import EstablishedState
from .FinWait2State import FinWait2State
from .ClosingState import ClosingState

class FinWait1State(EstablishedState):
    def on_ack(self, packet, addr):
        header = packet.header
        super().on_ack(packet, addr)
        if header.ack_number == self.context.seq_number:
            logging.warning("FIN confirmado. Aguardando FIN do peer...")
            self.transition(FinWait2State)

    def on_fin(self, packet, addr):
        header = packet.header
        logging.warning("FIN recebido em FIN_WAIT_1. Encerrando...")
        self.context.ack_number = c_uint16(header.seq_number + 1).value
        self.context.send_ack()
        self.transition(ClosingState)

