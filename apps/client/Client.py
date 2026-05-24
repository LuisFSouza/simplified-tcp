import os
import logging
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

log_path = os.path.join(ROOT_DIR, "cliente_log.txt")
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
	handlers=[
		logging.FileHandler(log_path, mode="w", encoding="utf-8"),
		logging.StreamHandler(sys.stdout),
	],
)

from tcp.api.SimplifiedTCP import SimplifiedTCP

client = SimplifiedTCP("127.0.0.1", 3000)
client.get_state().connect("127.0.0.1", 3001)

logging.warning("Cliente enviando dados...")
data = os.urandom(1024 * 500)  
client.send_and_wait(data)

logging.warning("Transmissao concluida. Fechando conexao...")
client.close()

logging.warning("Gerando metricas...")
client_metrics_path = os.path.join(ROOT_DIR, "metrics-client.png")
client.plot_metrics(output_path=client_metrics_path, show=False)