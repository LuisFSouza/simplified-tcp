# Relatório de CWND vs Tempo

O gráfico de métricas é gerado automaticamente pelo `tcp.workers.MetricsCollector` na chamada `SimplifiedTCP.plot_metrics()`.
Ele inclui a plotagem de `cwnd` e `ssthresh` ao longo do tempo.

## Comportamento observado

- CWND inicial é `MSS = 1024 bytes`.
- Em `SlowStart`, a cada ACK recebido a janela cresce em `MSS` bytes.
- Quando `cwnd >= ssthresh` (inicial de `15360 bytes`), o controle muda para `CongestionAvoidance`.
- Em `CongestionAvoidance`, o crescimento por ACK é aproximado por `(MSS^2) / cwnd`, ou seja, um aumento mais lento e linear no longo prazo.
- O mecanismo de perda é baseado em timeout: se um pacote fica sem ACK por `0.5 s`, ele é retransmitido.
- No timeout, o protocolo reduz `ssthresh = max(cwnd/2, MSS)`, reinicia `cwnd = MSS` e retorna a `SlowStart`.

## Desempenho sob diferentes condições de perda

- Com perda baixa ou zero, o CWND sobe rapidamente e alcança a fase de `CongestionAvoidance`, produzindo throughput mais alto e menos retransmissões.
- Com perda moderada (por exemplo, `ack_drop_rate = 0.2`), a perda de ACKs causa timeouts frequentes.
  - O CWND sofre quedas abruptas para `MSS` e precisa recomeçar a partir de `SlowStart`.
  - Isso produz uma forma de onda típica de `sawtooth` no gráfico de CWND.
  - O throughput efetivo cai porque o protocolo passa mais tempo em recuperação.
- Com perda alta, o protocolo tende a permanecer mais tempo em `SlowStart`, reduzindo a janela de envio média e aumentando o número total de retransmissões.

## Reproduzir e comparar

Para comparar condições de perda, altere o parâmetro `ack_drop_rate` em `apps/server/Server.py`:

```python
server = SimplifiedTCP("127.0.0.1", 3001, 0.2)  # 20% de perda de ACK
```

Use valores como `0.0`, `0.1`, `0.2` ou `0.5` e execute novamente o servidor e o cliente.

## Arquivos gerados

- Exemplo de plot criado nesta execução: `metrics-1779060707.9865332.png`

## Conclusão

A implementação mostra um controle de congestionamento típico de TCP simplificado: crescimento exponencial em `SlowStart`, transição para crescimento mais linear em `CongestionAvoidance` e retração rápida em caso de perda.
A perda de ACKs é traduzida em timeouts e perda de janela, o que reduz sensivelmente o desempenho em condições com perda maior.
