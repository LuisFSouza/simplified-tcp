import logging
import threading
import time
from ctypes import c_uint16

class RetransmitWorker:
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
                    if self.context.send_buffer: 
                        base = self.context.send_base
                        sorted_seqs = sorted(self.context.send_buffer.keys(), key=lambda seq: c_uint16(seq - base).value)
                        
                        oldest_seq = sorted_seqs[0]
                        packet, timestamp = self.context.send_buffer[oldest_seq]
                        
                        if time.time() - timestamp > self.timeout_interval:
                            logging.warning(f"TIMEOUT: Retransmitindo pacote com seq {oldest_seq}")
                            self.context.send_buffer[oldest_seq] = (packet, time.time())
                            self.context.socket.sendto(packet.to_bytes(), self.context.remote_addr)
                            
                            self.context.dup_ack_count = 0
                            self.context.last_ack_number = None
                            
                            self.context.congestion_control.timeout()
                            self.context.metrics.record_retransmit()
            time.sleep(self.tick_interval)
