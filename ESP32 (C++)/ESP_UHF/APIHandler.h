#ifndef API_HANDLER_H
#define API_HANDLER_H

#include <Arduino.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <map>
#include <tuple>
#include <list>

#define username "esp32-staging-pos"
#define password "Tyco1234!"

std::map<String, String> get_tokens();
std::map<String, String> handle_tokens_response(String response);
std::tuple<std::map<String, String>, String> get_access_token(std::map<String, String> tokens);
std::map<String, String> refresh_tokens(String refresh_token);
int postPosTransaction(String access_token, String epc);
StaticJsonDocument<200> getPosTransactionHeaders(String access_token);
StaticJsonDocument<200> getPosPayload(String epc);

#endif