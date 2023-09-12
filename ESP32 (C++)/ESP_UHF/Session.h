#ifndef SESSION_H
#define SESSION_H

#include "APIHandler.h"
#include "Uhf.h"

class Session {
  public:
    Session(int r, int d, int c){
      request_interval = r;
      debounce_interval = d;
      clear_interval = c;
    }
  
    void set_request(int value) { request_interval = value; }
    void set_debounce(int value) { debounce_interval = value; }
    void set_clear(int value) { clear_interval = value; }
    void renew_token();
    void process_epcs();
    void send_epcs();
    void expiredAndInfo();

    int request_interval, debounce_interval, clear_interval;

    std::map<String, String> tokens;
    std::list<String> incoming_tags;
    std::list<String> expired_tags;
    std::map<String, std::tuple<int, int>> table;

    String access_token;
};

#endif