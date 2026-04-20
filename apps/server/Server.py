import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tcp.api.SimplifiedTCP import SimplifiedTCP

server = SimplifiedTCP("127.0.0.1", 3001, 0.2)  # 20% de perda de ACK

logging.warning("Servidor iniciado. Aguardando conexão...")
server.listen_until_peer_closes()

logging.warning("Conexão fechada. Plotando métricas...")
server.plot_metrics()