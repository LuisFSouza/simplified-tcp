import logging
from .TCPState import TCPState


class LastAckState(TCPState):
    def on_ack(self, packet, addr, event):
        if event.ack_number == self.context.seq_number:
            logging.warning("ACK do FIN recebido. Encerrando conexao...")
            self._finalize_close()
        else:
            logging.warning("ACK inesperado em LAST_ACK. Ignorando...")

    def _finalize_close(self):
        with self.context.lock:
            self.context.send_buffer.clear()
            self.context.send_base = self.context.seq_number
            self.context.remote_addr = None
        if self.context.is_listening:
            from .ListenState import ListenState
            self.transition(ListenState)
        else:
            from .ClosedState import ClosedState
            self.transition(ClosedState)
