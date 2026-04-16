from .TCPState import TCPState
from .EstablishedState import EstablishedState
import logging

class SynReceivedState(TCPState):
    def on_ack(self, packet, addr, event):
        logging.warning(f"Recebendo pacote em estado SYN-RECEIVED de {addr}")
        logging.warning(f"Flags: {event.flags_text()}")
        if event.ack_number == self.context.seq_number:
            with self.context.lock:
                self.context.send_buffer.clear()
                self.context.send_base = event.ack_number
            logging.warning("Transição para estado ESTABLISHED.")
            self.transition(EstablishedState)
        else:
            logging.warning("ACK invalido no SYN-RECEIVED, ignorando.")

