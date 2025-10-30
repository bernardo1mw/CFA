/**
 * XIAO ESP32-S3 Sense — TESTE: Captura 1 frame no setup e envia à API (multipart/form-data)
 * Requisitos (Arduino IDE):
 *   - Placa: Seeed XIAO ESP32S3 (ou ESP32S3 Dev Module)
 *   - Tools -> PSRAM: Enabled (idealmente 80 MHz)
 *   - Tools -> Partition Scheme: Default 4MB with spiffs (ou outra válida)
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

// ====== VL53L0X ======

#include "Adafruit_VL53L0X.h"
Adafruit_VL53L0X lox= Adafruit_VL53L0X();

// ====== MODELO DA PLACA/CÂMERA ======
#define CAMERA_MODEL_XIAO_ESP32S3
#include "camera_pins.h"

// ====== Wi-Fi ======
const char* WIFI_SSID     = "lab8";
const char* WIFI_PASSWORD = "lab8arduino";

// ====== API (use IP/hostname da rede, NÃO localhost) ======
const char* API_POST_IMAGE_URL   = "http://10.8.10.102:8000/api/v1/placas/upload_image";
const char* API_POST_CLEAR_URL   = "http://10.8.10.102:8000/api/v1/placas/clear"; // POST em /clear/{placa_id}
const char* API_AUTH_HEADER_KEY  = "Authorization";
const char* API_AUTH_HEADER_VAL  = ""; // ex.: "Bearer abc123" (ou deixe vazio)

// Ajuste:
const char* HOST = "10.8.10.102";   // IP do seu servidor (não use localhost)
const uint16_t PORT = 8000;
const char* HEALTH_PATH = "/api/v1/health";      // mude para /health se tiver

// ====== Histerese + debounce ======
enum class PresenceState : uint8_t { ABSENT = 0, PRESENT = 1 };

const uint16_t ENTER_THRESHOLD_MM = 900;   // entrou (dist < 900)
const uint16_t EXIT_THRESHOLD_MM  = 1200;  // saiu  (dist > 1200)

const uint32_t MIN_PRESENCE_MS = 5000;   // precisa manter presença por 5 s
const uint32_t MIN_ABSENCE_MS  = 5000;   // precisa manter ausência por 5 s

PresenceState currentState = PresenceState::ABSENT;
uint32_t stateChangeCandidateAt = 0;
String placa_id = "";
// --- util de memória (opcional) ---
static void printMem() {
  size_t dram   = heap_caps_get_free_size(MALLOC_CAP_8BIT);
  size_t spiram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
  Serial.printf("[MEM] DRAM=%u | PSRAM=%u | psramFound()=%d\n",
                (unsigned)dram, (unsigned)spiram, (int)psramFound());
}

// ====== Inicialização da câmera (PSRAM/SVGA como alvo) ======
static bool initCamera_PSRAM() {
  camera_config_t cfg = {};
  cfg.ledc_channel = LEDC_CHANNEL_0;
  cfg.ledc_timer   = LEDC_TIMER_0;

  cfg.pin_d0       = Y2_GPIO_NUM;
  cfg.pin_d1       = Y3_GPIO_NUM;
  cfg.pin_d2       = Y4_GPIO_NUM;
  cfg.pin_d3       = Y5_GPIO_NUM;
  cfg.pin_d4       = Y6_GPIO_NUM;
  cfg.pin_d5       = Y7_GPIO_NUM;
  cfg.pin_d6       = Y8_GPIO_NUM;
  cfg.pin_d7       = Y9_GPIO_NUM;
  cfg.pin_xclk     = XCLK_GPIO_NUM;
  cfg.pin_pclk     = PCLK_GPIO_NUM;
  cfg.pin_vsync    = VSYNC_GPIO_NUM;
  cfg.pin_href     = HREF_GPIO_NUM;
  cfg.pin_sccb_sda = SIOD_GPIO_NUM;
  cfg.pin_sccb_scl = SIOC_GPIO_NUM;
  cfg.pin_pwdn     = PWDN_GPIO_NUM;   // pode ser -1
  cfg.pin_reset    = RESET_GPIO_NUM;  // pode ser -1

  cfg.xclk_freq_hz = 20000000;
  cfg.pixel_format = PIXFORMAT_JPEG;

  cfg.frame_size   = FRAMESIZE_SVGA;       // 800x600 (bom para OCR)
  cfg.jpeg_quality = 12;                   // 10..16 (menor = melhor qualidade)
  cfg.fb_count     = 2;                    // 2 buffers
  cfg.grab_mode    = CAMERA_GRAB_LATEST;
  cfg.fb_location  = CAMERA_FB_IN_PSRAM;   // usar PSRAM

  printMem();
  esp_err_t err = esp_camera_init(&cfg);
  if (err != ESP_OK) {
    Serial.printf("[CAM] init PSRAM/SVGA falhou: 0x%x\n", err);
    return false;
  }
  Serial.println("[CAM] PSRAM/SVGA ok.");
  return true;
}

// ====== Fallback (DRAM/VGA/1 buffer) para garantir envio ======
static bool initCamera_Fallback_DRAM() {
  camera_config_t cfg = {};
  cfg.ledc_channel = LEDC_CHANNEL_0;
  cfg.ledc_timer   = LEDC_TIMER_0;

  cfg.pin_d0       = Y2_GPIO_NUM;
  cfg.pin_d1       = Y3_GPIO_NUM;
  cfg.pin_d2       = Y4_GPIO_NUM;
  cfg.pin_d3       = Y5_GPIO_NUM;
  cfg.pin_d4       = Y6_GPIO_NUM;
  cfg.pin_d5       = Y7_GPIO_NUM;
  cfg.pin_d6       = Y8_GPIO_NUM;
  cfg.pin_d7       = Y9_GPIO_NUM;
  cfg.pin_xclk     = XCLK_GPIO_NUM;
  cfg.pin_pclk     = PCLK_GPIO_NUM;
  cfg.pin_vsync    = VSYNC_GPIO_NUM;
  cfg.pin_href     = HREF_GPIO_NUM;
  cfg.pin_sccb_sda = SIOD_GPIO_NUM;
  cfg.pin_sccb_scl = SIOC_GPIO_NUM;
  cfg.pin_pwdn     = PWDN_GPIO_NUM;
  cfg.pin_reset    = RESET_GPIO_NUM;

  cfg.xclk_freq_hz = 20000000;
  cfg.pixel_format = PIXFORMAT_JPEG;

  cfg.frame_size   = FRAMESIZE_VGA;        // 640x480
  cfg.jpeg_quality = 14;                   // arquivo menor
  cfg.fb_count     = 1;                    // 1 buffer
  cfg.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
  cfg.fb_location  = CAMERA_FB_IN_DRAM;    // DRAM

  printMem();
  esp_err_t err = esp_camera_init(&cfg);
  if (err != ESP_OK) {
    Serial.printf("[CAM] init DRAM/VGA falhou: 0x%x\n", err);
    return false;
  }
  Serial.println("[CAM] DRAM/VGA ok (fallback).");
  return true;
}

// ====== Wi-Fi ======
static void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("[WiFi] Conectando");
  while (WiFi.status() != WL_CONNECTED) { delay(400); Serial.print("."); }
  Serial.println();
  Serial.printf("[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
}

// ====== HTTP Functions ======
bool probe_http_get() {
  WiFiClient client;
  HTTPClient http;
  String url = String("http://") + HOST + ":" + PORT + HEALTH_PATH;

  http.setConnectTimeout(8000);
  http.setTimeout(10000);
  http.useHTTP10(true);            // evita chunked (alguns servidores não curtem)
  http.setReuse(false);

  Serial.printf("[PROBE] GET %s\n", url.c_str());
  if (!http.begin(client, url)) {
    Serial.println("[PROBE] http.begin() falhou");
    return false;
  }
  int code = http.GET();
  Serial.printf("[PROBE] resp=%d\n", code);
  if (code > 0) {
    String body = http.getString();
    Serial.printf("[PROBE] body len=%d\n", body.length());
  }
  http.end();
  return (code > 0);
}


static String extractJsonStringByKey(const String& json, const char* key) {
  String pattern = String("\"") + key + "\":";
  int p = json.indexOf(pattern);
  if (p < 0) return "";
  p += pattern.length();
  // pular espaços
  while (p < (int)json.length() && json[p] == ' ') p++;
  // pular aspas iniciais
  if (p < (int)json.length() && json[p] == '"') p++;
  int start = p;
  int end = json.indexOf('"', start);
  if (end < 0) return "";
  return json.substring(start, end);
}

static bool postJpegMultipart(const uint8_t* buf, size_t len) {
  const String boundary    = "----xiaoS3BoundaryA1B2C3";
  const String contentType = "multipart/form-data; boundary=" + boundary;

  const String head =
      "--" + boundary + "\r\n"
      "Content-Disposition: form-data; name=\"image\"; filename=\"frame.jpg\"\r\n"
      "Content-Type: image/jpeg\r\n\r\n";
  const String tail = "\r\n--" + boundary + "--\r\n";

  const size_t totalLen = head.length() + len + tail.length();
  uint8_t* body = (uint8_t*) malloc(totalLen);
  if (!body) { Serial.println("[HTTP] malloc falhou"); return false; }

  memcpy(body, head.c_str(), head.length());
  memcpy(body + head.length(), buf, len);
  memcpy(body + head.length() + len, tail.c_str(), tail.length());

  WiFiClient client;
  HTTPClient http;
  if (!http.begin(client, API_POST_IMAGE_URL)) {
    Serial.println("[HTTP] begin() falhou");
    free(body);
    return false;
  }
  http.addHeader("Content-Type", contentType);
  if (API_AUTH_HEADER_VAL && strlen(API_AUTH_HEADER_VAL) > 0) {
    http.addHeader(API_AUTH_HEADER_KEY, API_AUTH_HEADER_VAL);
  }

  int code = http.POST(body, totalLen);
  bool ok = (code >= 200 && code < 300);
  Serial.printf("[HTTP] POST code=%d ok=%d total=%u bytes\n", code, ok, (unsigned)totalLen);
  if (ok) {
    String resp = http.getString();
    Serial.printf("[HTTP] resp: %s\n", resp.c_str());
    String id = extractJsonStringByKey(resp, "_id");
    if (id.length() == 0) {
      id = extractJsonStringByKey(resp, "id");
    }
    if (id.length() > 0) {
      placa_id = id;
      Serial.printf("[HTTP] extracted id=%s\n", placa_id.c_str());
    } else {
      Serial.println("[HTTP] id não encontrado no JSON");
    }
  }
  http.end();
  free(body);
  return ok;
}

static void sendImage() {
  probe_http_get();
  // 1) Captura UMA foto e envia
  Serial.println("[CAPTURE] Capturando frame...");
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[CAPTURE] fb_get falhou. Abortando.");
    while (true) delay(1000);
  }
  Serial.printf("[CAPTURE] %ux%u | %u bytes\n", fb->width, fb->height, fb->len);

  Serial.println("[UPLOAD] Enviando para API (multipart)...");
  bool ok = postJpegMultipart(fb->buf, fb->len);
  esp_camera_fb_return(fb);

  Serial.println(ok ? "[UPLOAD] OK" : "[UPLOAD] FALHOU");
}

static bool postClear() {
  WiFiClient client;
  HTTPClient http;
  http.setConnectTimeout(8000);
  http.setTimeout(10000);
  http.useHTTP10(true);
  http.setReuse(false);

  if (placa_id.length() == 0) {
    Serial.println("[CLEAR] placa_id vazio. Faça upload primeiro.");
    return false;
  }

  String url = String(API_POST_CLEAR_URL) + "/" + placa_id;
  if (!http.begin(client, url)) {
    Serial.println("[HTTP] begin() falhou");
    return false;
  }

  if (API_AUTH_HEADER_VAL && strlen(API_AUTH_HEADER_VAL) > 0) {
    http.addHeader(API_AUTH_HEADER_KEY, API_AUTH_HEADER_VAL);
  }
  http.addHeader("Content-Length", "0");

  int code = http.POST((uint8_t*)NULL, 0); // POST sem body
  bool ok = (code >= 200 && code < 300);
  Serial.printf("[HTTP] POST CLEAR code=%d ok=%d url=%s\n", code, ok, url.c_str());
  http.end();
  return ok;
}

static void sendClear() {
  probe_http_get();
  Serial.println("[CLEAR] Enviando para API...");
  bool ok = postClear();
  Serial.println(ok ? "[CLEAR] OK" : "[CLEAR] FALHOU");
}


// ====== Laser Functions ======
static uint16_t readDistanceMm() {
  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false);
  if (measure.RangeStatus != 4) return (uint16_t)measure.RangeMilliMeter;
  return 8191; // fora de alcance
}

static PresenceState evalPresence(uint16_t dmm) {
  if (currentState == PresenceState::ABSENT) {
    return (dmm < ENTER_THRESHOLD_MM) ? PresenceState::PRESENT
                                      : PresenceState::ABSENT;
  } else {
    return (dmm > EXIT_THRESHOLD_MM) ? PresenceState::ABSENT
                                     : PresenceState::PRESENT;
  }
}

static void checkState(uint16_t dmm) {
  PresenceState target = evalPresence(dmm);
  uint32_t now = millis();

  if (target != currentState) {
    if (stateChangeCandidateAt == 0) stateChangeCandidateAt = now;

    uint32_t dwell = now - stateChangeCandidateAt;
    bool stable = false;
    if (currentState == PresenceState::ABSENT && target == PresenceState::PRESENT) {
      stable = (dwell >= MIN_PRESENCE_MS);
    } else if (currentState == PresenceState::PRESENT && target == PresenceState::ABSENT) {
      stable = (dwell >= MIN_ABSENCE_MS);
    }

    if (stable) {
      PresenceState prev = currentState;
      currentState = target;
      stateChangeCandidateAt = 0;

      if (prev == PresenceState::ABSENT && currentState == PresenceState::PRESENT) {
        Serial.printf("[STATE] CHEGADA: d=%u mm\n", dmm);
        sendImage();
      } else if (prev == PresenceState::PRESENT && currentState == PresenceState::ABSENT) {
        Serial.printf("[STATE] SAIDA:   d=%u mm\n", dmm);
        sendClear();
        
      }
    }
  } else {
    stateChangeCandidateAt = 0;
  }
}

// ====== Inicialização da câmera e laser ======
static void initCamera() {
    // 1) Inicializa câmera (preferindo PSRAM/SVGA; cai para DRAM/VGA se falhar)
    bool camOK = false;
    if (psramFound()) {
      Serial.println("[INFO] PSRAM detectada. Tentando SVGA/2 buffers em PSRAM...");
      camOK = initCamera_PSRAM();
      if (!camOK) {
        Serial.println("[WARN] Falhou com PSRAM. Tentando fallback DRAM/VGA...");
        camOK = initCamera_Fallback_DRAM();
      }
    } else {
      Serial.println("[WARN] PSRAM NAO detectada. Indo direto para DRAM/VGA.");
      camOK = initCamera_Fallback_DRAM();
    }
    if (!camOK) {
      Serial.println("[ERRO] Câmera não inicializou. Abortando.");
      while (true) delay(1000);
    }
  
    // 2) Conecta Wi-Fi
    connectWiFi();
}

static void initLaser() {
  if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X"));
    while(1);
  }
  Serial.println("[READY] VL53L0X ok");
}


// Separa o log periódico de distância/estado
static void logDistance(uint16_t dmm) {
  static uint32_t lastLog = 0;
  if (millis() - lastLog > 500) {
    lastLog = millis();
    Serial.printf("[DIST] %u mm | estado=%s\n",
                  dmm,
                  currentState == PresenceState::PRESENT ? "PRESENT" : "ABSENT");
  }
}


// ====== Main functions ======
void setup() {
  Serial.begin(115200);
  delay(300);
  initCamera();
  initLaser();

}

void loop() {
  uint16_t dmm = readDistanceMm();
  checkState(dmm);
  logDistance(dmm);
  delay(20); // ~50 Hz
}
