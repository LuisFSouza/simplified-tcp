import logging
from ctypes import c_uint16
from .TCPState import TCPState
from .TimeWaitState import TimeWaitState

class FinWait2State(TCPState):
    def on_fin(self, packet, addr, event):
        logging.warning("FIN recebido em FIN_WAIT_2. Encerrando conexao...")
        self.context.ack_number = c_uint16(event.seq_number + 1).value
        self.context.send_ack()
        self.transition(TimeWaitState)

    def on_ack(self, packet, addr, event):
        logging.info("ACK recebido em FIN_WAIT_2. Ignorando...")

