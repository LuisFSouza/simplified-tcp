import logging
import threading
import time


class RetransmitController:
    def __init__(self, context, timeout_interval=0.5, tick_interval=0.1):
        self.context = context
        self.timeout_interval = timeout_interval
        self.tick_interval = tick_interval
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        while not self.context.stop_threads:
            with self.context.lock:
                for seq in list(self.context.send_buffer.keys()):
                    packet, timestamp = self.context.send_buffer[seq]
                    if time.time() - timestamp > self.timeout_interval:
                        logging.warning(f"Retransmitindo pacote seq={seq}")
                        self.context.send_buffer[seq] = (packet, time.time())
                        self.context.socket.sendto(packet.to_bytes(), self.context.remote_addr)
                        self.context.congestion_control.timeout()
                        self.context.metrics.record_retransmit()
            time.sleep(self.tick_interval)
