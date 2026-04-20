import os
import logging
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tcp.api.SimplifiedTCP import SimplifiedTCP

client = SimplifiedTCP("127.0.0.1", 3000)
client.get_state().connect("127.0.0.1", 3001)

logging.warning("Cliente enviando dados...")
data = os.urandom(1024 * 100)  
client.send_and_wait(data)

logging.warning("Transmissao concluida. Fechando conexao...")
client.close()

logging.warning("Gerando metricas...")
client.plot_metrics()