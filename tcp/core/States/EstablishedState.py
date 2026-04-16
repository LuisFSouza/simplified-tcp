import logging
import time
from .TCPState import TCPState
from ctypes import c_uint16
from .CloseWaitState import CloseWaitState

class EstablishedState(TCPState):
    def on_ack(self, packet, addr, event):
        received_ack = event.ack_number
        logging.info(f"ACK recebido: {received_ack}")
        keys_to_remove = []
        acked_bytes = 0
        for seq in self.context.send_buffer.keys():
            if c_uint16(seq - self.context.send_base).value < c_uint16(received_ack - self.context.send_base).value:
                keys_to_remove.append(seq)

        now = time.time()
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

    def on_data(self, packet, addr, event):
        if event.data_len > 0:
            logging.info(f"Dados recebidos ({event.data_len} bytes). Enviando ACK...")
            self.context.ack_number = c_uint16(event.seq_number + event.data_len).value
            self.context.send_ack()
            self.context.metrics.record_received(event.data_len)

    def on_fin(self, packet, addr, event):
        logging.warning("FIN recebido. Encerrando conexão...")
        self.context.ack_number = c_uint16(event.seq_number + 1).value
        self.context.send_ack()
        self.transition(CloseWaitState)