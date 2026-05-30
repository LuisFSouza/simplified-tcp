# Relatório

## Gráficos da execução do TCP.

![Gráfico](exemplo.png)

## Cenário

A execução é sobre o envio de 1024000 bytes do cliente para o servidor. A simulação aqui é com um buffer de recepção de tamanho de 16384 bytes.

### Comportamento observado
- Considerando o gráfico `Congestion Window`, rapidamente `cwnd` ultrapassa o valor máximo do buffer do receptor. Isso significa, que bem no inicio da transmissão (quando `cwnd` < 16384), quem determina a janela de transmissão é o controle de congestionamento. A partir do momento em que `cwnd` > 16384, quem começa a controlar a janela de transmissão é o controle de fluxo, ja que o tamanho máximo do buffer é 16384, e o `cwnd` tem valor superior. Isso é oque demonstra o gráfico `Transmission Blocks`, onde bem no começo o controle de congestionamento é quem bloqueia a transmissão, e após `cwnd` > 16384, o controle de fluxo passa a bloquear.
- No gráfico `Window Probes Sent`, também podemos ver o envio de pacotes de sondagem ao servidor quando este indicava que seu buffer estava cheio, para que o cliente pudesse receber "novas informações" do estado do buffer do receptor.
- No gráfico `Bytes In Flight`, podemos ver que a quantidade de  bytes em voo respeitou o limite do buffer do receptor de 16384 bytes. Não houve extrapolação desse valor, mesmo em momentos que, o `cwnd` do controle de congestionamento (podendo ser visto no gráfico `Congestion Window`) tivesse um valor muito superior.

Podemos perceber assim que o Controle de Fluxo funcionou adequadamente, com o cliente conseguindo respeitar os limites do servidor, e entregando os pacotes esperados ao servidor.