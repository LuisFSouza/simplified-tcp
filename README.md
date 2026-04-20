# TCP simplificado sobre UDP

## Visao geral
Este projeto implementa um TCP simplificado sobre UDP, com handshake, controle de congestao, retransmissao e coleta de metricas. Ha um cliente e um servidor de exemplo para exercitar o protocolo.

## Como executar (exemplo)
- Servidor: `python apps/server/Server.py`
- Cliente: `python apps/client/Client.py`

Fluxo atual:
- o servidor entra em listen e aguarda o cliente fechar a conexao via `listen_until_peer_closes()`;
- o cliente envia os dados com `send_and_wait()` e depois encerra com `close()`.

## Estrutura principal
- Cliente de exemplo: [apps/client/Client.py](apps/client/Client.py)
- Servidor de exemplo: [apps/server/Server.py](apps/server/Server.py)
- Implementacao do protocolo: [tcp](tcp)

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

## Simulacao de perda de ACK
O servidor aceita a taxa de perda de ACK no construtor de [tcp/api/SimplifiedTCP.py](tcp/api/SimplifiedTCP.py). Exemplo:
- `server = SimplifiedTCP("127.0.0.1", 3001, 0.2)`

O terceiro parametro representa a taxa de perda simulada de ACKs.

## Fechamento de conexao
- Fechamento ativo: ESTABLISHED -> FIN_WAIT_1 -> FIN_WAIT_2 -> TIME_WAIT -> CLOSED.
- Fechamento passivo: ESTABLISHED -> CLOSE_WAIT -> (app chama close) -> LAST_ACK -> CLOSED.
- Fechamento simultaneo: ESTABLISHED -> FIN_WAIT_1 -> CLOSING -> TIME_WAIT -> CLOSED.

## Classes

### API
- `SimplifiedTCP`: fachada do protocolo; coordena socket, estados, controle de congestao, buffers, workers e metricas. Expõe helpers de alto nivel como `send_and_wait()` e `listen_until_peer_closes()`. Arquivo: [tcp/api/SimplifiedTCP.py](tcp/api/SimplifiedTCP.py)

### Ciclo de vida e envio
- `SendWorker`: consome a fila de envio, divide payloads, respeita o `cwnd` e registra metricas. Arquivo: [tcp/workers/SendWorker.py](tcp/workers/SendWorker.py)
- `ReceiveWorker`: recebe pacotes UDP e delega o tratamento ao estado atual. Arquivo: [tcp/workers/ReceiveWorker.py](tcp/workers/ReceiveWorker.py)
- `RetransmitController`: monitora timeouts no send buffer e retransmite, atualizando controle de congestao e metricas. Arquivo: [tcp/workers/RetransmitWorker.py](tcp/workers/RetransmitWorker.py)
- `MetricsCollector`: coleta series temporais (cwnd, ssthresh, bytes in flight, fila) e gera graficos. Arquivo: [tcp/workers/MetricsCollector.py](tcp/workers/MetricsCollector.py)

### Pacotes
- `Header`: representa o header fixo e valida campos (seq, ack, recv_window, flags, len). Arquivo: [tcp/core/Packet/Header.py](tcp/core/Packet/Header.py)
- `Packet`: encapsula header e payload e faz (de)serializacao. Arquivo: [tcp/core/Packet/Packet.py](tcp/core/Packet/Packet.py)

### Controle de congestao
- `CongestionControl`: mantem `cwnd`/`ssthresh` e delega para o estado atual. Arquivo: [tcp/core/Congestion/CongestionControl.py](tcp/core/Congestion/CongestionControl.py)
- `CongestionControlState`: interface base para estados de controle de congestao. Arquivo: [tcp/core/Congestion/CongestionControlState.py](tcp/core/Congestion/CongestionControlState.py)
- `SlowStart`: crescimento exponencial por ACK ate `ssthresh`; em timeout reinicia. Arquivo: [tcp/core/Congestion/SlowStart.py](tcp/core/Congestion/SlowStart.py)
- `CongestionAvoidance`: crescimento aditivo por ACK; em timeout reinicia. Arquivo: [tcp/core/Congestion/CongestionAvoidance.py](tcp/core/Congestion/CongestionAvoidance.py)

### Estados do TCP
- `TCPState`: base da FSM; roteia SYN/ACK/FIN/DATA para handlers. Arquivo: [tcp/core/States/TCPState.py](tcp/core/States/TCPState.py)
- `ClosedState`: estado inicial; inicia conexao (cliente) ou entra em listen. Arquivo: [tcp/core/States/ClosedState.py](tcp/core/States/ClosedState.py)
- `ListenState`: aguarda SYN e responde com SYN-ACK. Arquivo: [tcp/core/States/ListenState.py](tcp/core/States/ListenState.py)
- `SynSentState`: cliente apos enviar SYN; valida SYN-ACK e conclui handshake. Arquivo: [tcp/core/States/SynSentState.py](tcp/core/States/SynSentState.py)
- `SynReceivedState`: servidor apos enviar SYN-ACK; aguarda ACK final. Arquivo: [tcp/core/States/SynReceivedState.py](tcp/core/States/SynReceivedState.py)
- `EstablishedState`: troca de dados e ACKs; alimenta controle de congestao e metricas. Arquivo: [tcp/core/States/EstablishedState.py](tcp/core/States/EstablishedState.py)
- `FinWait1State`: fechamento ativo apos enviar FIN; aguarda ACK/FIN. Arquivo: [tcp/core/States/FinWait1State.py](tcp/core/States/FinWait1State.py)
- `FinWait2State`: aguarda FIN do peer apos ACK do FIN. Arquivo: [tcp/core/States/FinWait2State.py](tcp/core/States/FinWait2State.py)
- `CloseWaitState`: fechamento passivo apos receber FIN; aguarda a aplicacao chamar `close()`. Arquivo: [tcp/core/States/CloseWaitState.py](tcp/core/States/CloseWaitState.py)
- `ClosingState`: FIN simultaneo; aguarda ACK do seu FIN antes do TIME_WAIT. Arquivo: [tcp/core/States/ClosingState.py](tcp/core/States/ClosingState.py)
- `LastAckState`: espera ACK do FIN no fechamento passivo. Arquivo: [tcp/core/States/LastAckState.py](tcp/core/States/LastAckState.py)
- `TimeWaitState`: estado final do fechamento ativo; aguarda um tempo antes de liberar recursos. Arquivo: [tcp/core/States/TimeWaitState.py](tcp/core/States/TimeWaitState.py)
