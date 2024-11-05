#include <ArduinoJson.h>

// Parameters
const float tank_height1 = 6.0;    // Height of the tank in cm (adjust according to actual tank height)
const float tank_height2 = 8.0;    // Height of the tank in cm (adjust according to actual tank height)
const float systemVoltage = 5.0;  // Voltage of the system (change according to your local voltage)

// Pin definitions for ultrasonic sensors, pumps, and current sensors for two homes
const int trigPinHome1 = 9;
const int echoPinHome1 = 10;
const int trigPinHome2 = 11;
const int echoPinHome2 = 12;
const int pumpRelayPinHome1 = 7;
const int pumpRelayPinHome2 = 8; 
const int currentSensorPinHome1 = A0;
const int currentSensorPinHome2 = A1;

// Variables for sensor readings and pump control
long durationHome1, durationHome2;
float distanceHome1, distanceHome2;
float currentHome1, currentHome2;
float powerHome1, powerHome2;  // Power in watts
float currentWaterLevelHome1, currentWaterLevelHome2;

// AS712 sensor calibration constants
const float voltageRef = 5.0;
const int adcResolution = 1024;
const float zeroCurrentOffset = 2.5;
const float sensitivity = 0.185;

// Flag to check if a pump is running
bool isPump1Running = false;
bool isPump2Running = false;

void setup() {
  Serial.begin(9600);

  // Setup pin modes for sensors and relays
  pinMode(trigPinHome1, OUTPUT);
  pinMode(echoPinHome1, INPUT);
  pinMode(trigPinHome2, OUTPUT);
  pinMode(echoPinHome2, INPUT);
  pinMode(pumpRelayPinHome1, OUTPUT);
  pinMode(pumpRelayPinHome2, OUTPUT);

  // Turn pumps off initially
  digitalWrite(pumpRelayPinHome1, HIGH);  // Relay is off when HIGH (pump OFF)
  digitalWrite(pumpRelayPinHome2, HIGH);  // Relay is off when HIGH (pump OFF)
  delay(10000);
}

void loop() {
  // Measure water levels for both homes
  distanceHome1 = measureDistance(trigPinHome1, echoPinHome1);
  distanceHome2 = measureDistance(trigPinHome2, echoPinHome2);

  // Control the pumps based on water levels
  controlPumps();

  // Measure current consumption for both homes
  currentHome1 = measureCurrent(currentSensorPinHome1);
  currentHome2 = measureCurrent(currentSensorPinHome2);

  // Calculate power usage for both homes
  powerHome1 = currentHome1 * systemVoltage;  // Power (Watts) = Current (Amps) * Voltage (Volts)
  powerHome2 = currentHome2 * systemVoltage;

  // Send the measured data to Python via Serial in JSON format
  sendJsonData();

  delay(2000);  // Wait for 1 second before the next loop
}

// Function to measure distance using an ultrasonic sensor
int measureDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  float distanceCm = duration * 0.034 / 2;
  return distanceCm;
}

// Function to measure current using the AS712 current sensor
float measureCurrent(int currentSensorPin) {
  int sensorValue = analogRead(currentSensorPin);
  float sensorVoltage = sensorValue * (voltageRef / adcResolution);
  float current = (sensorVoltage - zeroCurrentOffset) / sensitivity;

  // Prevent negative current readings
  if (current < 0) {
    current = 0;
  }
  return current;
}

// Function to control pumps based on water levels and priority
void controlPumps() {
  // Calculate water levels in percentage based on tank height
  currentWaterLevelHome1 = ((tank_height1 - distanceHome1) / tank_height1) * 100;  // Water level as a percentage
  currentWaterLevelHome2 = ((tank_height2 - distanceHome2) / tank_height2) * 100;

  Serial.println("Distance1: " + String(distanceHome1));
  Serial.println("Distance2: " + String(distanceHome2));

  // Home 1 pump control
  if (currentWaterLevelHome1 >= 0 && currentWaterLevelHome1 < 50 && !isPump2Running) {
    // Turn on pump for Home 1 if water level is below 50%
    digitalWrite(pumpRelayPinHome1, LOW);
    isPump1Running = true;
  } else {
    // Turn off pump for Home 1 if water level reaches 90%
    digitalWrite(pumpRelayPinHome1, HIGH);
    isPump1Running = false;
  }

  // Home 2 pump control
  if (currentWaterLevelHome2>=0 && currentWaterLevelHome2 < 60 && !isPump1Running) {
    // Turn on pump for Home 2 if water level is below 50%
    digitalWrite(pumpRelayPinHome2, LOW);
    isPump2Running = true;
  } else {
    // Turn off pump for Home 2 if water level reaches 90%
    digitalWrite(pumpRelayPinHome2, HIGH);
    isPump2Running = false;
  }
}

// Function to send data as JSON via Serial
void sendJsonData() {
  StaticJsonDocument<512> jsonDoc1;
  StaticJsonDocument<512> jsonDoc2;

  // Home 1 data
  jsonDoc1["HomeID"] = 1;
  jsonDoc1["CurrentWaterLevel"] = currentWaterLevelHome1;
  jsonDoc1["ElectricityUsage"] = currentHome1;
  jsonDoc1["Power"] = powerHome1;
  jsonDoc1["PumpRunningStatus"] = isPump1Running;

  // Home 2 data
  jsonDoc2["HomeID"] = 2;
  jsonDoc2["CurrentWaterLevel"] = currentWaterLevelHome2;
  jsonDoc2["ElectricityUsage"] = currentHome2;
  jsonDoc2["Power"] = powerHome2;
  jsonDoc2["PumpRunningStatus"] = isPump2Running;

  // Serialize JSON data and send via Serial
  serializeJson(jsonDoc1, Serial);
  Serial.println();
  serializeJson(jsonDoc2, Serial);
  Serial.println();
}
