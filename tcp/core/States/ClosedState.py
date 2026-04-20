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
            self.transition(SynSentState)

    def listen(self):
        self.context.is_listening = True
        self.transition(ListenState)
