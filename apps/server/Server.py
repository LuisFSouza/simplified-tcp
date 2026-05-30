import logging
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

log_path = os.path.join(ROOT_DIR, "server_log.txt")
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
	handlers=[
		logging.FileHandler(log_path, mode="w", encoding="utf-8"),
		logging.StreamHandler(sys.stdout),
	],
)

from tcp.api.SimplifiedTCP import SimplifiedTCP

server = SimplifiedTCP("127.0.0.1", 3001, max_window_size = 16384)
logging.warning("Servidor iniciado. Aguardando conexão...")
server.listen_until_peer_closes(app_processing_delay=0.02)

logging.warning("Quantidade de pacotes recebidos: %d", server.received_packet_count)

logging.warning("Conexão fechada. Plotando métricas...")
server_metrics_path = os.path.join(ROOT_DIR, "metrics-server.png")
server.plot_metrics(output_path=server_metrics_path, show=False)