import logging
import random
import socket
import threading
import time
import queue
from tcp.core.Congestion.CongestionControl import CongestionControl
from tcp.core.ConnectionLifecycle import ConnectionLifecycle
from tcp.workers.MetricsCollector import MetricsCollector
from tcp.core.PacketBuilder import PacketBuilder
from tcp.workers.ReceiveWorker import ReceiveWorker
from tcp.workers.RetransmitWorker import RetransmitController
from tcp.workers.SendWorker import SendWorker
from tcp.core.States.ClosedState import ClosedState
from tcp.core.States.CloseWaitState import CloseWaitState
from tcp.core.States.FinWait1State import FinWait1State
from tcp.core.States.LastAckState import LastAckState

class SimplifiedTCP:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))
        self.mss = 1024
        self.remote_addr = None
        self.seq_number = 0 # Numero de sequência (byte do próximo pacote a ser enviado)
        self.ack_number = 0 # Número de reconhecimento (byte do próximo pacote esperado)

        self.congestion_control = CongestionControl(mss=self.mss)
        self.send_queue = queue.Queue()
        self.lock = threading.RLock()
        self.stop_threads = False
        self.is_listening = False
        self.ack_drop_enabled = False
        self.ack_drop_rate = 0.0
        self.send_base = 0          # Primeiro não confirmado
        self.send_buffer = {}       # Buffer de pacotes enviados mas não confirmados, mapeando seq_number para (packet, timestamp)
        self.metrics = MetricsCollector()
        self.state = ClosedState(self)
        self.packet_builder = PacketBuilder(self)
        self.send_worker = SendWorker(self)
        self.receive_worker = ReceiveWorker(self)
        self.retransmit_controller = RetransmitController(self)
        self.lifecycle = ConnectionLifecycle(
            self,
            self.receive_worker,
            self.send_worker,
            self.retransmit_controller,
        )
        self.lifecycle.start()
        
    
    def set_state(self, new_state):
        self.state = new_state

    def get_state(self):
        return self.state

    def send_data(self, data: bytes):
        self.send_queue.put(data)

    def set_remote(self, ip, port):
        self.remote_addr = (ip, port)

    def send_packet(self, payload=b"", ack_flag=0, syn_flag=0, fin_flag=0):
        return self.packet_builder.send_packet(
            payload=payload,
            ack_flag=ack_flag,
            syn_flag=syn_flag,
            fin_flag=fin_flag,
        )

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

    def retransmit_first_buffered(self, predicate=None):
        with self.lock:
            for seq, (pkt, _) in self.send_buffer.items():
                if predicate is None or predicate(pkt):
                    self.send_buffer[seq] = (pkt, time.time())
                    return pkt
        return None

    def send_ack(self):
        if self.ack_drop_enabled and self.ack_drop_rate > 0:
            if random.random() < self.ack_drop_rate:
                logging.warning("Simulando perda de ACK.")
                return None
        return self.packet_builder.send_ack()

    def send_syn(self):
        return self.packet_builder.send_syn()

    def send_fin(self):
        return self.packet_builder.send_fin()

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
        self.lifecycle.stop(join_timeout=1.0)
        logging.warning("Conexão finalizada com sucesso.")

    def plot_metrics(self):
        self.metrics.plot()