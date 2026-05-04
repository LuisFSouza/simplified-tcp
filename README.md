# TCP simplificado sobre UDP

## Visao geral
Este projeto implementa um TCP simplificado sobre UDP, com handshake, controle de congestionamento, retransmissao e coleta de metricas. Ha um cliente e um servidor de exemplo para exercitar o protocolo.

## Como executar

### Instalação
- Requer Python 3.12.7 (`python --version`).
- Instale dependencias: `pip install -r requirements.txt`

### Execução
- Servidor: `python apps/server/Server.py`
- Cliente: `python apps/client/Client.py`

## Parametros da especificacao
- Header: 8 bytes (seq, ack, recv_window, len, flags).
- Tamanho maximo do pacote: 1032 bytes (header 8 + payload 1024).
- MSS: 1024 bytes.
- CWND inicial: 1024 bytes.
- SSTHRESH inicial: 15360 bytes.
- RTO: 500 ms.

## Metricas e graficos
- CWND e SSTHRESH ao longo do tempo.
- Bytes in flight.
- RTT (ms).
- Throughput (bytes/s).
- Retransmissoes acumuladas.
- Acked bytes e received bytes (acumulado).
