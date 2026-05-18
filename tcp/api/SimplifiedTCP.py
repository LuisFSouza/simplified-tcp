import logging
import random
import socket
import threading
import time
import queue
from ctypes import c_uint16
from tcp.core.Congestion.CongestionControl import CongestionControl
from tcp.workers.MetricsCollector import MetricsCollector
from tcp.workers.ReceiveWorker import ReceiveWorker
from tcp.workers.RetransmitWorker import RetransmitWorker
from tcp.workers.SendWorker import SendWorker
from tcp.core.States.ClosedState import ClosedState
from tcp.core.States.CloseWaitState import CloseWaitState
from tcp.core.States.FinWait1State import FinWait1State
from tcp.core.States.LastAckState import LastAckState
from tcp.core.Packet.Packet import Packet

class SimplifiedTCP:
    def __init__(self, ip, port, ack_drop_rate=0.0, drop_packet_for_index = None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))
        self.remote_addr = None
        self.seq_number = 0
        self.ack_number = 0
        self.send_base = 0
        self.send_buffer = {}
        self.receive_buffer = {}
        self.application_buffer = queue.Queue()
        self.send_queue = queue.Queue()
        self.lock = threading.RLock()
        self.stop_threads = False
        self.is_listening = False
        
        self.last_ack_number = None;
        self.dup_ack_count = 0
        
        # Simulações de timeout e 3 acks duplicados
        self.ack_drop_enabled = False
        if (ack_drop_rate > 0):
            self.ack_drop_enabled = True
        self.ack_drop_rate = ack_drop_rate
        
        self.drop_data_for_packet_index = drop_packet_for_index
        self.received_packet_count = 0
    
        
        self.congestion_control = CongestionControl()
        self.metrics = MetricsCollector()
        self.state = ClosedState(self)
        self.send_worker = SendWorker(self)
        self.receive_worker = ReceiveWorker(self)
        self.retransmit_worker = RetransmitWorker(self)
        self.start_workers()

    def set_state(self, new_state):
        self.state = new_state

    def get_state(self):
        return self.state

    def send_data(self, data: bytes):
        self.send_queue.put(data)

    def set_remote(self, ip, port):
        self.remote_addr = (ip, port)

    def send_packet(self, payload=b"", ack_flag=0, syn_flag=0, fin_flag=0):
        if self.remote_addr is None:
            logging.error("Endereco remoto nao definido")
            raise ValueError("Endereco remoto nao definido")

        packet = Packet(
            payload=payload,
            seq_number=self.seq_number,
            ack_number=self.ack_number,
            ack_flag=ack_flag,
            syn_flag=syn_flag,
            fin_flag=fin_flag,
        )

        self._advance_seq(len(payload), syn_flag, fin_flag)

        if ack_flag != 1:
            self.buffer_packet(packet)

        self.socket.sendto(packet.to_bytes(), self.remote_addr)
        self._log_send(packet)
        return packet

    def buffer_packet(self, packet):
        with self.lock:
            self.send_buffer[packet.header.seq_number] = (packet, time.time())

    def pop_first_buffered(self, predicate=None):
        with self.lock:
            for seq, (pkt, _) in list(self.send_buffer.items()):
                if predicate is None or predicate(pkt):
                    del self.send_buffer[seq]
                    return seq, pkt
        return None, None

    def _advance_seq(self, payload_len, syn_flag, fin_flag):
        if syn_flag or fin_flag:
            self.seq_number = c_uint16(self.seq_number + 1).value
        elif payload_len > 0:
            self.seq_number = c_uint16(self.seq_number + payload_len).value

    def _log_send(self, packet):
        header = packet.header
        logging.warning(
            f"Enviou pacote para {self.remote_addr} | "
            f"seq={header.seq_number} "
            f"ack={header.ack_number} "
            f"ack_flag={header.ack_flag} "
            f"syn_flag={header.syn_flag} "
            f"fin_flag={header.fin_flag} "
            f"len_data={header.len_data}"
        )

    def send_ack(self):
        if self.ack_drop_enabled and self.ack_drop_rate > 0:
            if random.random() < self.ack_drop_rate:
                logging.warning("Simulando perda de ACK.")
                return None
        return self.send_packet(ack_flag=1)

    def send_syn_ack(self):
        return self.send_packet(syn_flag=1, ack_flag=1)

    def send_syn(self):
        return self.send_packet(syn_flag=1)

    def send_fin(self):
        return self.send_packet(fin_flag=1)

    def close(self, graceful=True, timeout=1.0):
        logging.warning("Fechando conexão...")
        if graceful and self.remote_addr is not None:
            try:
                self.send_fin()
                if isinstance(self.state, CloseWaitState):
                    self.set_state(LastAckState(self))
                else:
                    self.set_state(FinWait1State(self))
                deadline = time.time() + timeout
                while time.time() < deadline and not isinstance(self.state, ClosedState):
                    time.sleep(0.01)
            except Exception as e:
                logging.error(f"Erro ao iniciar fechamento: {e}")

        self.stop_threads = True
        try:
            self.socket.close()
        except Exception as e:
            logging.error(f"Erro ao fechar socket: {e}")
        self.stop_workers()
        logging.warning("Conexão finalizada com sucesso.")

    def start_workers(self):
        self.receive_worker.start()
        self.send_worker.start()
        self.retransmit_worker.start()

    def stop_workers(self, join_timeout=1.0):
        for thread in (self.receive_worker.thread, self.send_worker.thread, self.retransmit_worker.thread):
            thread.join(timeout=join_timeout)

    def plot_metrics(self):
        self.metrics.plot()

    def listen_until_peer_closes(self, poll_interval=0.05):
        self.get_state().listen()
        while not isinstance(self.state, CloseWaitState):
            time.sleep(poll_interval)
        self.close()
    
    def send_and_wait(self, data: bytes, poll_interval=0.05):
        self.send_data(data)
        self.wait_for_send_complete(poll_interval=poll_interval)

    def wait_for_send_complete(self, poll_interval=0.05):
        while True:
            with self.lock:
                done = self.send_queue.empty() and len(self.send_buffer) == 0
            if done:
                return
            time.sleep(poll_interval)
