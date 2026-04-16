import time
import threading
import queue
from ctypes import c_uint16
from tcp.core.States.EstablishedState import EstablishedState

class SendWorker:
    def __init__(self, context):
        self.context = context
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        while not self.context.stop_threads:
            if not self._is_established():
                time.sleep(0.05)
                continue
            data = self._get_next_payload()
            if data is None:
                continue

            chunks = self._split_data(data)
            for i, chunk in enumerate(chunks):
                with self.context.lock:
                    bytes_in_flight = self._bytes_in_flight()
                    self._record_metrics(bytes_in_flight)

                    if not self._can_send(bytes_in_flight, len(chunk)):
                        self._enqueue_remaining(chunks, i)
                        break

                    self.context.send_packet(payload=chunk)

    def _is_established(self):
        return isinstance(self.context.state, EstablishedState)

    def _bytes_in_flight(self):
        return c_uint16(self.context.seq_number - self.context.send_base).value

    def _record_metrics(self, bytes_in_flight):
        self.context.metrics.record_window(
            cwnd=self.context.congestion_control.get_cwnd(),
            ssthresh=self.context.congestion_control.ssthresh,
            bytes_in_flight=bytes_in_flight,
            send_queue_size=self.context.send_queue.qsize(),
        )

    def _can_send(self, bytes_in_flight, chunk_len):
        return bytes_in_flight + chunk_len <= self.context.congestion_control.get_cwnd()

    def _split_data(self, data):
        return [data[i:i + self.context.mss] for i in range(0, len(data), self.context.mss)]

    def _enqueue_remaining(self, chunks, start_index):
        remaining = b"".join(chunks[start_index:])
        if remaining:
            self.context.send_queue.put(remaining)

    def _get_next_payload(self):
        try:
            return self.context.send_queue.get(timeout=0.1)
        except queue.Empty:
            return None
