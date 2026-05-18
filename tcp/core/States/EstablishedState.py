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
        
        if (self.context.last_ack_number is None or (
                c_uint16(received_ack - self.context.last_ack_number).value > 0 and
                received_ack != self.context.last_ack_number)):
            self.context.last_ack_number = received_ack
            self.context.dup_ack_count = 0
            
            keys_to_remove = []
            for seq in self.context.send_buffer.keys():
                if c_uint16(seq - self.context.send_base).value < c_uint16(received_ack - self.context.send_base).value:
                    keys_to_remove.append(seq)

            acked_bytes = 0
            for seq in sorted(keys_to_remove, key=lambda seq: c_uint16(seq - self.context.send_base).value):
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
            
        elif received_ack == self.context.last_ack_number:
            if self.context.send_buffer:
                lost_seq = min(self.context.send_buffer.keys(), key=lambda seq: c_uint16(seq - self.context.send_base).value)
                pkt, _ = self.context.send_buffer[lost_seq]
                
                if c_uint16(received_ack - lost_seq).value == 0:
                    self.context.dup_ack_count += 1
                    logging.warning(f"ACK Duplicado detectado para seq {received_ack}. Contagem: {self.context.dup_ack_count}/3")
                    
                    if self.context.dup_ack_count == 3:
                        logging.warning(f"Três ACKs duplicados detectados para seq {received_ack}!")
                        self.context.congestion_control.three_dup_ack()
                        logging.warning(f"Disparando Fast Retransmit para seq {lost_seq}")
                        self.context.socket.sendto(pkt.to_bytes(), self.context.remote_addr)
                        
                        for seq in self.context.send_buffer.keys():
                            p, _ = self.context.send_buffer[seq]
                            self.context.send_buffer[seq] = (p, time.time())
                            
                        self.context.metrics.record_retransmit()
                        
                    elif self.context.dup_ack_count > 3:
                        self.context.congestion_control.additional_dup_ack()

    def on_data(self, packet, addr):
        self.context.received_packet_count += 1
        header = packet.header
        
        if (self.context.drop_data_for_packet_index is not None and 
            self.context.received_packet_count == self.context.drop_data_for_packet_index):
            logging.warning(f"Simulando perda de pacote #{self.context.received_packet_count} (seq={header.seq_number})")
            return
        
        if header.len_data > 0:
            expected_seq = self.context.ack_number
            self.context.receive_buffer[header.seq_number] = packet.payload
            if(header.seq_number == expected_seq):
                logging.info(f"Dados recebidos na ordem (seq {header.seq_number}). Enviando ACK normal...")
            else:
                logging.info(f"Dados recebidos fora de ordem (seq {header.seq_number}). Enviando ACK duplicado para seq {expected_seq}...")
            
            while self.context.ack_number in self.context.receive_buffer:
                payload = self.context.receive_buffer[self.context.ack_number]
                self.context.application_buffer.put(payload)
                del self.context.receive_buffer[self.context.ack_number]
                self.context.ack_number = c_uint16(self.context.ack_number + len(payload)).value 
                logging.info(f"Dados entregues até seq {self.context.ack_number}")
            self.context.send_ack()
            self.context.metrics.record_received(header.len_data)

    def on_fin(self, packet, addr):
        header = packet.header
        logging.warning("FIN recebido. Encerrando conexão...")
        self.context.ack_number = c_uint16(header.seq_number + 1).value
        self.context.send_ack()
        self.transition(CloseWaitState)