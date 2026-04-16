import logging
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tcp.api.SimplifiedTCP import SimplifiedTCP
from tcp.core.States.CloseWaitState import CloseWaitState

ACK_LOSS_ENABLED = True
ACK_LOSS_RATE = 0.2

server = SimplifiedTCP("127.0.0.1", 3001)
server.get_state().listen()
if ACK_LOSS_ENABLED:
    server.ack_drop_enabled = True
    server.ack_drop_rate = ACK_LOSS_RATE
    logging.warning(f"Simulando perda de ACKs: taxa={ACK_LOSS_RATE}")

logging.warning("Servidor aguardando pacotes...")

try:
    while True:
        time.sleep(0.1)
        if isinstance(server.get_state(), CloseWaitState):
            logging.warning("Servidor em CLOSE_WAIT. Fechando...")
            server.close()
            break
except KeyboardInterrupt:
    logging.warning("Encerrando servidor...")
    server.close()