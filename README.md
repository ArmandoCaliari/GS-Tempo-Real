# GS-Tempo-Real

Explicação da Implementação
O projeto desenvolvido tem como objetivo monitorar, em tempo real, a rede Wi-Fi à qual o dispositivo está conectado, verificando se ela pertence a uma lista de redes seguras previamente cadastradas. Caso o dispositivo se conecte a uma rede não autorizada, o sistema gera um alerta visual (LED) e um registro no log serial.
Para isso, o sistema foi implementado no ESP32 utilizando o sistema operacional de tempo real FreeRTOS, que permite dividir o código em tarefas independentes que rodam de forma paralela.
Estrutura geral do sistema
O código é dividido em três tarefas principais, além do bloco setup() de inicialização e do loop() vazio (já que o FreeRTOS gerencia as tarefas).
1. scannerTask (Tarefa de varredura)
Essa tarefa é responsável por simular a leitura do nome da rede Wi-Fi (SSID) à qual o dispositivo está conectado.
 Como o projeto está rodando em modo de simulação (por exemplo, no Wokwi), o código usa um vetor simPool com vários nomes de redes.
 A cada intervalo de tempo (SCAN_INTERVAL_MS), um novo SSID é selecionado e enviado para a fila (wifiQueue), que será lida pela próxima tarefa.
Função principal: gerar e enviar o nome da rede atual.


Prioridade: média (2).


Recurso usado: fila (xQueueSend).
2. checkTask (Tarefa de verificação)
Essa é a tarefa mais importante do sistema.
 Ela fica constantemente verificando se há novos SSIDs na fila (wifiQueue).
 Quando recebe um SSID, ela compara com a lista de redes seguras (safeNetworks).
 Essa lista contém cinco nomes de redes autorizadas.
Se o nome recebido estiver na lista, o sistema considera a rede segura e pisca o LED verde (LED_OK).
 Se o nome não estiver na lista, o sistema entende que a rede é insegura e acende o LED vermelho (LED_ALERT), além de registrar no log serial uma mensagem de alerta.
Função principal: validar se a rede é segura.


Prioridade: alta (3).


Recursos usados: fila (xQueueReceive), semáforo (xSemaphoreTake / xSemaphoreGive), LED e log via Serial.println().
3. inputTask (Tarefa de entrada de comandos)
Essa tarefa é opcional e serve apenas para permitir uma interação manual via monitor serial.
 Ao pressionar a tecla 'r', o índice da simulação (simIndex) é incrementado, forçando a troca para o próximo SSID na lista de simulação.
Função principal: simular troca manual de rede.


Prioridade: baixa (1).


Recurso usado: comunicação serial (Serial.read()).
Técnicas de robustez utilizadas
Isolamento de tarefas:
Cada função do sistema (escaneamento, verificação e entrada de comando) roda em uma tarefa separada, com prioridade diferente.
Assim, se uma travar, as outras continuam funcionando.
Proteção com semáforo (mutex):
O acesso à lista de redes seguras é protegido por um mutex (xSemaphoreTake / xSemaphoreGive), evitando corrupção de dados em acessos simultâneos.
Timeout na fila:
 Caso a tarefa checkTask não receba dados da fila dentro de 5 segundos, ela registra um aviso de timeout.Isso impede que o sistema fique preso indefinidamente esperando dados que talvez nunca cheguem.

Estratégia de recuperação (Watchdog simulado):
Se três timeouts consecutivos forem detectados, o sistema entende que há uma falha grave e reinicia automaticamente o ESP32 usando esp_restart(). Essa é uma forma simples de implementar uma recuperação automática em caso de travamento.
