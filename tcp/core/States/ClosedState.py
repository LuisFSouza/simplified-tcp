from .TCPState import TCPState
import logging
import random
from .SynSentState import SynSentState
from .ListenState import ListenState

class ClosedState(TCPState):
    def connect(self, ip, port):
        logging.warning(f"Iniciando conexão com {ip}:{port}")
        self.context.is_listening = False
        self.context.set_remote(ip, port)
        with self.context.lock:
            self.context.seq_number = random.randint(0, 65535)
            self.context.send_base = self.context.seq_number
            self.context.send_syn()
            logging.warning("Transição para estado SYN_SENT")
            self.transition(SynSentState)

    def on_unexpected(self, packet, addr, event):
        logging.warning("Pacote recebido em estado CLOSED. Ignorando...")

    def listen(self):
        logging.warning("Transição para estado LISTEN")
        self.context.is_listening = True
        self.transition(ListenState)