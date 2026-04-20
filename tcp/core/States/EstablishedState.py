import logging
import time
from .TCPState import TCPState
from ctypes import c_uint16
from .CloseWaitState import CloseWaitState

class EstablishedState(TCPState):
    def on_ack(self, packet, addr):
        now = time.time()
        header = packet.header
        received_ack = header.ack_number
        logging.info(f"ACK recebido: {received_ack}")
        keys_to_remove = []
        acked_bytes = 0
        for seq in self.context.send_buffer.keys():
            if c_uint16(seq - self.context.send_base).value < c_uint16(received_ack - self.context.send_base).value:
                keys_to_remove.append(seq)

        for seq in sorted(keys_to_remove):
            pkt, sent_at = self.context.send_buffer[seq]
            payload_len = len(pkt.payload)
            fin_consumes = 1 if pkt.header.fin_flag == 1 else 0
            packet_len = payload_len + fin_consumes
            acked_bytes += packet_len
            self.context.send_base = c_uint16(seq + packet_len).value
            if sent_at is not None:
                self.context.metrics.record_rtt(now - sent_at)
            del self.context.send_buffer[seq]
        self.context.congestion_control.ack_receive()
        self.context.metrics.record_acked(acked_bytes)

    def on_data(self, packet, addr):
        header = packet.header
        if header.len_data > 0:
            logging.info(
                f"Dados recebidos ({header.len_data} bytes). Enviando ACK...")
            self.context.ack_number = c_uint16(
                header.seq_number + header.len_data).value
            self.context.send_ack()
            self.context.metrics.record_received(header.len_data)

    def on_fin(self, packet, addr):
        header = packet.header
        logging.warning("FIN recebido. Encerrando conexão...")
        self.context.ack_number = c_uint16(header.seq_number + 1).value
        self.context.send_ack()
        self.transition(CloseWaitState)
