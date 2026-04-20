import logging
import threading
from ctypes import c_uint16
from .TCPState import TCPState
from .ClosedState import ClosedState

class TimeWaitState(TCPState):
    def __init__(self, context, duration=1.0):
        super().__init__(context)
        self.duration = duration
        self._timer = None
        self._start_timer()

    def on_fin(self, packet, addr):
        header = packet.header
        logging.warning("FIN recebido em TIME_WAIT. Reenviando ACK...")
        self.context.ack_number = c_uint16(header.seq_number + 1).value
        self.context.send_ack()
        self._start_timer()

    def _start_timer(self):
        if self._timer is not None:
            self._timer.cancel()
        self._timer = threading.Timer(self.duration, self._finalize_close)
        self._timer.daemon = True
        self._timer.start()

    def _finalize_close(self):
        with self.context.lock:
            self.context.send_buffer.clear()
            self.context.send_base = self.context.seq_number
            self.context.remote_addr = None
            self.context.is_listening = False
            self.transition(ClosedState)
