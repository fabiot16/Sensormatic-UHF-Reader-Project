#include "APIHandler.h"

HTTPClient http;
String auth_api_url = "https://auth.sea.stg.cloud.sensormatic.com/realms/sensormatic/protocol/openid-connect/token";

std::map<String, String> get_tokens() {
  
  http.begin(auth_api_url);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  
  String auth_login_body = "client_id=smartexit-api&grant_type=password&username=esp32-staging-pos&password=Tyco1234!";

  int statusCode = http.POST((uint8_t *)auth_login_body.c_str(), auth_login_body.length());

  Serial.print("LoginAPI status code: " + String(statusCode));

  if (statusCode == 200){
    String response = http.getString();
    return handle_tokens_response(response);
  }
  
  http.end();
  return std::map<String, String>();
}

std::map<String, String> handle_tokens_response(String response) {
  DynamicJsonDocument jsonDoc(1024);  // Adjust the size as needed
  DeserializationError error = deserializeJson(jsonDoc, response);

  std::map<String, String> tokens;

  if (error) {
    Serial.print("JSON parsing error: ");
    Serial.println(error.c_str());
  } else {
    String access_token = jsonDoc["access_token"].as<String>();
    String refresh_token = jsonDoc["refresh_token"].as<String>();
    int expires_in = jsonDoc["expires_in"].as<int>();
    int refresh_expires_in = jsonDoc["refresh_expires_in"].as<int>();

    tokens["access_token"] = jsonDoc["access_token"].as<String>();
    tokens["refresh_token"] = jsonDoc["refresh_token"].as<String>();
    tokens["expires_in"] = jsonDoc["expires_in"].as<String>();
    tokens["refresh_expires_in"] = jsonDoc["refresh_expires_in"].as<String>();
    tokens["request_time"] = millis();
  }

  return tokens;
}

std::tuple<std::map<String, String>, String> get_access_token(std::map<String, String> tokens) {
  
  int elapsed = millis()/1000 - tokens["request_time"].toInt();
  int expires_in = tokens["expires_in"].toInt();
  String access_token = tokens["access_token"];
  std::map<String, String> new_tokens;

  if (elapsed > expires_in) {
    Serial.println("Token is expired: " + String(elapsed) + " > " + String(expires_in) + ", request: " + String(tokens["request_time"]));
    new_tokens = refresh_tokens(tokens["refresh_token"]);
  }

  return std::make_tuple(new_tokens, access_token);
}

std::map<String, String> refresh_tokens(String refresh_token) {
  String auth_refresh_body = "client_id=smartexit-api&grant_type=refresh_token&refresh_token=" + refresh_token;
  http.begin(auth_api_url);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  int statusCode = http.POST((uint8_t*)auth_refresh_body.c_str(), auth_refresh_body.length());

  Serial.println("API Refresh Token status code: " + String(statusCode));

  if (statusCode == 200){
    String response = http.getString();
    return handle_tokens_response(response);
  }

  http.end();
  return std::map<String, String>();
}

int postPosTransaction(String access_token, String epc) {
  String api_header_json;
  serializeJson(getPosTransactionHeaders(access_token), api_header_json);
  String payload_json;
  serializeJson(getPosPayload(epc), payload_json);
  String URL = "https://sea.stg.cloud.sensormatic.com/v2/pos/transaction";

  http.begin(URL);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", "Bearer " + String(access_token));
  int statusCode = http.POST(payload_json);
  
  http.end();

  return statusCode;
}

StaticJsonDocument<200> getPosTransactionHeaders(String access_token) {
  StaticJsonDocument<200> header;

  header["Content-Type"] = "application/json";
  header["Authorization"] = "Bearer " + String(access_token);

  return header;
}

StaticJsonDocument<200> getPosPayload(String epc) {
  StaticJsonDocument<200> transaction_api_payload;

  struct tm timeinfo;
  getLocalTime(&timeinfo);

  char formatted_time[30];
  snprintf(formatted_time, sizeof(formatted_time),
           "%04d-%02d-%02dT%02d:%02d:%02d",
           timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
           timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);

  const char* values[] = {"sale", "return"};

  transaction_api_payload["timestamp"] = formatted_time;
  transaction_api_payload["siteCode"] = "Site 10";
  transaction_api_payload["posStation"] = "1";
  transaction_api_payload["cashier"] = "esp32";

  JsonArray items = transaction_api_payload.createNestedArray("items");
  JsonObject item = items.createNestedObject();

  item["type"] = values[random(2)];
  item["epc"] = epc;

  return  transaction_api_payload;
}