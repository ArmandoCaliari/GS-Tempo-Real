#include <WiFi.h>
#include <Arduino.h>

#define LED_ALERT 2
#define LED_OK 4
#define SCAN_INTERVAL_MS 4000

QueueHandle_t wifiQueue;
SemaphoreHandle_t safeListMutex;

String safeNetworks[] = {
  "CorpNet-01",
  "CorpNet-02",
  "Office_WiFi",
  "MinhaRedeTrabalho",
  "LabWiFi"
};
const int SAFE_NET_COUNT = 5;

String simPool[] = {
  "CorpNet-01",
  "FreeWiFi",
  "CorpNet-02",
  "RedeSecgura",
  "Office_WiFi",
  "MinhaRedeTrabalho"
};
int simIndex = 0;

void scannerTask(void *pv)
{
  while (1)
  {
    String currentSSID = simPool[simIndex];
    simIndex = (simIndex + 1) % 6;
    if (xQueueSend(wifiQueue, &currentSSID, pdMS_TO_TICKS(1000)) != pdTRUE) {
      Serial.println("[ERRO] Fila cheia - SSID perdido!");
    }
    Serial.println("[Scanner] SSID simulado: " + currentSSID);
    vTaskDelay(pdMS_TO_TICKS(SCAN_INTERVAL_MS));
  }
}

void checkTask(void *pv)
{
  String ssid;
  int timeoutCount = 0;

  while (1)
  {
    if (xQueueReceive(wifiQueue, &ssid, pdMS_TO_TICKS(5000)) == pdTRUE)
    {
      timeoutCount = 0;
      bool authorized = false;

      if (xSemaphoreTake(safeListMutex, pdMS_TO_TICKS(1000)) == pdTRUE)
      {
        for (int i = 0; i < SAFE_NET_COUNT; i++)
        {
          if (ssid == safeNetworks[i]) authorized = true;
        }
        xSemaphoreGive(safeListMutex);
      }
      else
      {
        Serial.println("[ERRO] Falha ao acessar lista segura (mutex timeout)");
      }

      if (!authorized)
      {
        Serial.printf("[%lu ms] ⚠️ ALERTA: REDE NAO AUTORIZADA -> %s\n", millis(), ssid.c_str());
        digitalWrite(LED_OK, LOW);
        for (int i = 0; i < 3; i++) {
          digitalWrite(LED_ALERT, HIGH);
          vTaskDelay(pdMS_TO_TICKS(200));
          digitalWrite(LED_ALERT, LOW);
          vTaskDelay(pdMS_TO_TICKS(200));
        }
      }
      else
      {
        Serial.printf("[%lu ms] [OK] Rede permitida: %s\n", millis(), ssid.c_str());
        for (int i = 0; i < 2; i++) {
          digitalWrite(LED_OK, HIGH);
          vTaskDelay(pdMS_TO_TICKS(150));
          digitalWrite(LED_OK, LOW);
          vTaskDelay(pdMS_TO_TICKS(150));
        }
      }
    }
    else
    {
      timeoutCount++;
      Serial.printf("[WARN] Nenhum SSID recebido (timeout %d)\n", timeoutCount);
      if (timeoutCount >= 3)
      {
        Serial.println("[RECUPERAÇÃO] Reiniciando sistema por inatividade...");
        esp_restart();
      }
    }
  }
}

void inputTask(void *pv)
{
  while (1)
  {
    if (Serial.available())
    {
      char c = Serial.read();
      if (c == 'r')
      {
        Serial.println("[CMD] Rotação manual do SSID simulada.");
        simIndex = (simIndex + 1) % 6;
      }
    }
    vTaskDelay(pdMS_TO_TICKS(200));
  }
}

void setup()
{
  Serial.begin(115200);
  pinMode(LED_ALERT, OUTPUT);
  pinMode(LED_OK, OUTPUT);

  wifiQueue = xQueueCreate(5, sizeof(String));
  safeListMutex = xSemaphoreCreateMutex();

  if (wifiQueue == NULL || safeListMutex == NULL)
  {
    Serial.println("[ERRO] Falha ao criar fila ou mutex!");
    while (1);
  }

  xTaskCreate(scannerTask, "scanner", 4096, NULL, 2, NULL);
  xTaskCreate(checkTask, "checker", 4096, NULL, 3, NULL);
  xTaskCreate(inputTask, "input", 4096, NULL, 1, NULL);

  Serial.println("[SISTEMA] Iniciado - Monitor de Redes Wi-Fi (modo simulado)");
}

void loop() {}
