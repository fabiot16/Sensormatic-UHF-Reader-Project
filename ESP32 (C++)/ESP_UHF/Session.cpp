#include "Session.h"

String epc;
std::tuple<int, int> values;
int last_seen;
int last_sent;

void Session::renew_token() {
  std::map<String, String> new_tokens;
  String access_tokens;

  std::tie(new_tokens, access_tokens) = get_access_token(tokens);

  if (new_tokens.empty()) {
    Serial.print("Fail to refresh tokens!");
    return;
  } else {
    tokens = new_tokens;
    access_token = access_token;
  }
}

void Session::expiredAndInfo() {
  int current_time = millis()/1000;
  std::list<String> expired_tags;

    for (const auto& entry : table) {
      const String& key = entry.first;
      const auto& tuple = entry.second;
      int last_seen = std::get<0>(tuple);
      int last_sent = std::get<0>(tuple);

      if (last_seen + clear_interval < current_time) {
          expired_tags.push_back(key);
          Serial.print("------- DELETED: ");
          Serial.println(key);
          continue;
      }

      Serial.print(key);
      Serial.print(" ");
      Serial.print(last_seen);
      Serial.print(" ");
      Serial.println(last_sent);
  }

  // Remove expired items from the table
  for (const auto &expired : expired_tags) {
      table.erase(expired);
  }
}

void Session::send_epcs() {
  for (String epc : incoming_tags) {
    int posRepsonse = postPosTransaction(access_token, epc);
  }

  //thread_info.onRun(expiredAndInfo);
  //thread_info.setInterval(0);
}

void Session::process_epcs() {
  int last_seen;
  int last_sent;

  if (!tokens.empty()) {
    if (!incoming_tags.empty()) {
      std::list<String> epcs = incoming_tags;
      std::map<String, std::tuple<int, int>> registry = table;
      int current_time = millis()/1000;

      for (String epc : epcs) {

        if (registry.find(epc) == registry.end()) {

          registry["epc"] = std::make_tuple(current_time, current_time);

        } else {

          std::tie(last_seen, last_sent) = registry["epc"];

          if (last_sent + debounce_interval < current_time) {
            last_sent = current_time;
            Serial.println("---------------SENT");
          }

          last_seen = current_time;
          registry["epc"] = std::make_tuple(last_seen, last_sent);
        }
      }

      Serial.println();Serial.println();

      incoming_tags = std::list<String>();
      table = registry;
    }
  }
}