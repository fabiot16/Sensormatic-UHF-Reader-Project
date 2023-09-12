#include <HardwareSerial.h>
#include <Arduino.h>
#include <time.h>
#include <map> 
#include <tuple>
#include <list>
#include <Thread.h>
#include "WiFiManager.h"
#include "Session.h"

//------------------------------------------------------------------------//

#define mySerial Serial2
#define BT1 5

// Create thread objects
//Thread receive_epcs = Thread();

Session session = Session(5, 10, 20);
int checkpoint = millis()/1000;

//Uncomment corresponding commands to configure UHF, more command can be added in UHF.h
//#define COMMANDS HARDWARE_VERSION
//#define COMMANDS MULTIPLE_READ
#define COMMANDS SINGLE_READ
//#define COMMANDS STOP_READ

void setup() {

  mySerial.begin(115200, SERIAL_8N1, 18, 17);
  Serial.begin(115200);
  mySerial.setTimeout(2000);
  
  SPIFFS.begin();

  pinMode(21,OUTPUT);
  digitalWrite(21,LOW); // LOW - to enable the module and HIGH to disable the module
  pinMode(BT1, INPUT);

  wificonfig();

  configTime(0, 0, "pool.ntp.org");

  //receive_epcs.onRun(receive_epcs);
  //receive_epcs.setInterval(3000);
}

void loop() {

  //if digitalRead(BT1){
    // Config page
    // update session values
  //}

  while (millis()/1000 < checkpoint + session.request_interval) {
    receive_epcs();
    delay(1);
  }

  checkpoint = millis()/1000;

  session.process_epcs();
}



void receive_epcs() {
  mySerial.write(COMMANDS, sizeof(COMMANDS)); // send command to UHF module for configuration
  delay(100);
  
  int len = mySerial.available();
  if (len > 0) {
    mySerial.readBytes(container, len); // Read Response from UHF module, and parse frame received
    frameParse(container, len); // This process done in Uhf.cpp file
  }
}

void wificonfig() {

  WiFi.mode(WIFI_STA);
  WiFiManager wifiManager;
  wifiManager.resetSettings();
  std::vector<const char *> menu = {"wifi", "config", "sep", "info", "exit"};
  
  // Tema escuro
  wifiManager.setMenu(menu);
  wifiManager.setClass("invert");

  bool res;
  res = wifiManager.autoConnect("SSRMTC", "password"); // password protected ap
  
  Serial.println("Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void config_rfid(){

  WiFiManager wifiManager;
  std::vector<const char *> menu = {"config", "erase", "sep", "info", "exit"};
  
  // Tema escuro
  wifiManager.setMenu(menu);
  wifiManager.setClass("invert");

  bool res;
  res = wifiManager.autoConnect("SSRMTC", "password"); // password protected ap
  
  Serial.println("Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}