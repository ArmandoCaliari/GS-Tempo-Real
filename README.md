# GS-Tempo-Real
Faculdade de Informática e Administração Paulista

Nome: Armando Caliari Silva			RM: 86765
Nome: Leandro Serrano Borloni 		RM: 86867
Nome: Henrique Montone Casagrande	RM:86932















Global Solution
SISTEMAS DE TEMPO REAL





















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
Link do github:
Prints da simulação:
Situação 1 — Rede Não Confiável (LED Vermelho)
Em outra etapa da simulação, o sistema detectou um SSID que não consta na lista de redes seguras. Como resposta, o monitor serial exibiu uma mensagem de alerta semelhante a:
[50500 ms] ⚠️ ALERTA: REDE NAO AUTORIZADA -> RedeSecgura
[Scanner] SSID simulado: RedeSecgura
Nessa situação, o LED vermelho foi acionado, piscando para sinalizar o risco. Esse comportamento representa uma condição de segurança comprometida, onde a rede detectada não é reconhecida como autorizada pelo sistema. O alerta serve para notificar o usuário e permitir que medidas preventivas sejam tomadas, como o bloqueio de conexão ou a revisão das redes disponíveis.




Situação 2 — Rede Confiável (LED Verde)
Na simulação apresentada, o sistema identificou a rede “Office_WiFi” como pertencente à lista de redes seguras. Isso pode ser observado na mensagem do monitor serial:
[49350 ms] [OK] Rede permitida: Office_WiFi
[Scanner] SSID simulado: Office_WiFi
Nesse momento, o LED verde foi acionado, indicando que o dispositivo está conectado a uma rede confiável e autorizada. Essa resposta visual confirma que o ambiente de comunicação é seguro, garantindo que a troca de dados ocorra dentro dos parâmetros esperados. Assim, o sistema reconhece que não há risco associado à rede atual, mantendo seu funcionamento normal.

