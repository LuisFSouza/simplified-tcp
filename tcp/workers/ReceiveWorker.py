import logging
import threading
from tcp.core.Packet.Packet import Packet

class ReceiveWorker:
    def __init__(self, context):
        self.context = context
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        while not self.context.stop_threads:
            try:
                self.receive_once()
            except OSError as exc:
                if self.context.stop_threads:
                    break
                logging.error(f"Erro no receive loop: {exc}")
            except Exception as exc:
                logging.error(f"Erro no receive loop: {exc}")

    def receive_once(self):
        packet, addr = self.receive_packet()
        with self.context.lock:
            self.context.state.receive(packet, addr)

    def receive_packet(self):
        data, addr = self.context.socket.recvfrom(65535)
        packet = Packet.from_bytes(data)

        if self.context.remote_addr is None:
            self.context.remote_addr = addr

        header = packet.header
        logging.warning(
            f"Recebeu pacote de {addr} | "
            f"seq={header.seq_number} "
            f"ack={header.ack_number} "
            f"ack_flag={header.ack_flag} "
            f"syn_flag={header.syn_flag} "
            f"fin_flag={header.fin_flag} "
            f"len_data={header.len_data}"
        )
        return packet, addr