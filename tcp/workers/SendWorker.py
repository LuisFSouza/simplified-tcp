import time
import threading
import queue
from ctypes import c_uint16
from tcp.core.States.EstablishedState import EstablishedState

class SendWorker:
    def __init__(self, context):
        self.context = context
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.mss = 1024
        self._pending = b""
        self._pending_lock = threading.Lock()

    def start(self):
        self.thread.start()

    def has_pending(self):
        with self._pending_lock:
            return bool(self._pending)

    # SendWorker.py
    def _run(self):
        while not self.context.stop_threads:
            if not self._is_established():
                time.sleep(0.05)
                continue

            with self._pending_lock:
                if not self._pending:
                    data = self._get_next_payload()
                    if data is None:
                        continue
                    self._pending = data

            with self.context.lock:
                bytes_in_flight = self._bytes_in_flight()
                cwnd = int(self.context.congestion_control.get_cwnd())

                # Registra métricas SEMPRE, independente de conseguir enviar
                self._record_metrics(bytes_in_flight)

                with self._pending_lock:
                    if not self._pending:
                        continue
                    chunk_size = min(self.mss, len(self._pending))

                if bytes_in_flight + chunk_size > cwnd:
                    time.sleep(0.001)
                    continue

                with self._pending_lock:
                    chunk = self._pending[:chunk_size]
                    self._pending = self._pending[chunk_size:]

                self.context.send_packet(payload=chunk)

    def _is_established(self):
        return isinstance(self.context.state, EstablishedState)

    def _bytes_in_flight(self):
        return c_uint16(self.context.seq_number - self.context.send_base).value

    def _record_metrics(self, bytes_in_flight):
        self.context.metrics.record_window(
            cwnd=self.context.congestion_control.get_cwnd(),
            ssthresh=self.context.congestion_control.get_ssthresh(),
            bytes_in_flight=bytes_in_flight,
            send_queue_size=self.context.send_queue.qsize(),
        )

    def _get_next_payload(self):
        try:
            return self.context.send_queue.get(timeout=0.1)
        except queue.Empty:
            return None