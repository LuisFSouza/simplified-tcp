import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tcp.api.SimplifiedTCP import SimplifiedTCP

server = SimplifiedTCP("127.0.0.1", 3001, drop_packet_for_index=500)  # 3 Acks duplicados para o pacote de índice 500
logging.warning("Servidor iniciado. Aguardando conexão...")
server.listen_until_peer_closes()

logging.warning("Quantidade de pacotes recebidos: %d", server.application_buffer.qsize())

logging.warning("Conexão fechada. Plotando métricas...")
server.plot_metrics()