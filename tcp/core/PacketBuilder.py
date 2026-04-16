import logging
from ctypes import c_uint16
from tcp.core.Packet.Packet import Packet

class PacketBuilder:
    def __init__(self, context):
        self.context = context

    def create_packet(self, payload=b"", ack_flag=0, syn_flag=0, fin_flag=0):
        payload = bytes(payload)
        packet = Packet(payload=payload)
        header = packet.header

        header.seq_number = self.context.seq_number
        header.ack_number = self.context.ack_number
        header.ack_flag = ack_flag
        header.syn_flag = syn_flag
        header.fin_flag = fin_flag
        header.len_data = len(payload)

        return packet

    def send_packet(self, payload=b"", ack_flag=0, syn_flag=0, fin_flag=0):
        if self.context.remote_addr is None:
            logging.error("Endereco remoto nao definido")
            raise ValueError("Endereco remoto nao definido")

        packet = self.create_packet(
            payload=payload,
            ack_flag=ack_flag,
            syn_flag=syn_flag,
            fin_flag=fin_flag,
        )

        self._advance_seq(len(payload), syn_flag, fin_flag)

        if ack_flag != 1:
            self.context.buffer_packet(packet)

        self.context.socket.sendto(packet.to_bytes(), self.context.remote_addr)
        self._log_send(packet)
        return packet

    def send_ack(self):
        return self.send_packet(ack_flag=1)

    def send_syn(self):
        return self.send_packet(syn_flag=1)

    def send_fin(self):
        return self.send_packet(fin_flag=1)

    def _advance_seq(self, payload_len, syn_flag, fin_flag):
        if syn_flag or fin_flag:
            self.context.seq_number = c_uint16(self.context.seq_number + 1).value
        elif payload_len > 0:
            self.context.seq_number = c_uint16(self.context.seq_number + payload_len).value

    def _log_send(self, packet):
        header = packet.header
        logging.warning(
            f"Enviou pacote para {self.context.remote_addr} | "
            f"seq={header.seq_number} "
            f"ack={header.ack_number} "
            f"ack_flag={header.ack_flag} "
            f"syn_flag={header.syn_flag} "
            f"fin_flag={header.fin_flag} "
            f"len_data={header.len_data}"
        )
