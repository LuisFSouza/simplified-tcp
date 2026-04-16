import logging
from .TCPState import TCPState


class CloseWaitState(TCPState):
    def on_ack(self, packet, addr, event):
        logging.info("ACK recebido em CLOSE_WAIT. Ignorando...")

    def on_fin(self, packet, addr, event):
        logging.warning("FIN duplicado em CLOSE_WAIT. Ignorando...")
