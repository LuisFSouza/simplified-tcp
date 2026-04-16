import os
import logging
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tcp.api.SimplifiedTCP import SimplifiedTCP

client = SimplifiedTCP("127.0.0.1", 3000)
client.get_state().connect("127.0.0.1", 3001)

logging.warning("Cliente enviando pacote...")
data = os.urandom(1024 * 10000)  
client.send_data(data)
while not client.send_queue.empty() or client.send_buffer:
    time.sleep(0.05)
logging.warning("Transmissao concluida. Fechando conexao...")
client.close()
logging.warning("Gerando metricas...")

client.plot_metrics()