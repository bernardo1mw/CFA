/**
 * TESTE 2 — VL53L0X + evalPresence (sem câmera, sem API)
 * Placa: Seeed XIAO ESP32-S3 Sense
 * - I2C em D4 (GPIO8) e D5 (GPIO9)
 * - Lê distância
 * - Aplica histerese + debounce
 * - Loga mudanças de estado (chegada/saída)
 */

#include <Arduino.h>
#include "Adafruit_VL53L0X.h"

// ====== I2C do XIAO ESP32-S3 Sense ======
//#define I2C_SDA 8   // D4
// #define I2C_SCL 9   // D5

Adafruit_VL53L0X lox= Adafruit_VL53L0X();

// ====== Histerese + debounce ======
enum class PresenceState : uint8_t { ABSENT = 0, PRESENT = 1 };

const uint16_t ENTER_THRESHOLD_MM = 900;   // entrou (dist < 900)
const uint16_t EXIT_THRESHOLD_MM  = 1200;  // saiu  (dist > 1200)

const uint32_t MIN_PRESENCE_MS = 5000;   // precisa manter presença por 5 s
const uint32_t MIN_ABSENCE_MS  = 5000;   // precisa manter ausência por 5 s

PresenceState currentState = PresenceState::ABSENT;
uint32_t stateChangeCandidateAt = 0;

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

void setup() {
  Serial.begin(115200);
  delay(200);
  if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X"));
    while(1);
  }
  Serial.println("[READY] Teste VL53L0X + evalPresence");
}

// Separa a lógica de verificação/estabilização de estado
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
      } else if (prev == PresenceState::PRESENT && currentState == PresenceState::ABSENT) {
        Serial.printf("[STATE] SAIDA:   d=%u mm\n", dmm);
      }
    }
  } else {
    stateChangeCandidateAt = 0;
  }
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

void loop() {
  uint16_t dmm = readDistanceMm();
  checkState(dmm);
  logDistance(dmm);
  delay(20); // ~50 Hz
}
