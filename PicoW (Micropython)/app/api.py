from random import choice
from ujson import loads, dumps
from utime import time, localtime
from urequests import post
from app.config import api_config_stg, auth_headers, auth_login_body

'''
#API functions
'''

def get_tokens():
    login_resp = post(api_config_stg['auth_api_url'], headers=auth_headers, data=auth_login_body)
    print('LoginAPI status code:'+ str(login_resp.status_code))
    return [str(login_resp.status_code), handle_tokens_response(login_resp)]

def refresh_tokens(refresh_token):
    auth_refresh_body = 'client_id=smartexit-api&grant_type=refresh_token&refresh_token=%s' % refresh_token
    refresh_resp = post(api_config_stg['auth_api_url'], headers=auth_headers, data=auth_refresh_body)
    print('API Refresh Token status code:'+ str(refresh_resp.status_code))
    return handle_tokens_response(refresh_resp)

def handle_tokens_response(token_resp):
    if token_resp.status_code == 200:
        response_json = loads(token_resp.text)  # Parse JSON response
        tokens = {
            'access_token' : response_json['access_token'],
            'refresh_token' : response_json['refresh_token'],
            'expires_in': response_json['expires_in'],
            'refresh_expires_in': response_json['refresh_expires_in'],
            'request_time' : time()
        }
        token_resp.close()
        del token_resp
        del response_json
        return tokens
    else:
        return None

def get_access_token(tokens):
    diff = time() - int(tokens['request_time'])
    expires_in = int(tokens['expires_in'])
    access_token = tokens['access_token']
    new_tokens = tokens
    if diff > expires_in:
        print(f"Token is expired: {diff} > {expires_in}, request: {tokens['request_time']}")
        new_tokens = refresh_tokens(tokens['refresh_token'])
    return new_tokens, access_token

def getPosTransactionHeaders(token):
    header = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer %s' % token
    }
    return header

def getPosPayload(epc):
    current_time = localtime()
    formatted_time = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
        current_time[0], current_time[1], current_time[2],
        current_time[3], current_time[4], current_time[5]
    )
    values = ["sale", "return"]
    random_value = choice(values)
    transaction_api_payload = {
        "timestamp": formatted_time,
        "siteCode": "Site 10",
        "posStation": "1",
        "cashier": "picow",
        "items": [
            {
                "type": random_value,
                "epc": epc
            }
        ]
    }
    return transaction_api_payload

def postPosTransaction(access_token,epc):
    api_header = getPosTransactionHeaders(access_token)
    payload = dumps(getPosPayload(epc))
    URL = api_config_stg['api_url']+"/v2/pos/transaction"
    try:
        return post(URL, headers=api_header, data=payload)
    except OSError as ex:
        print("Error occurred:", ex)
        return None

def handlePosApiResponse(response):
    if response.status_code == 204 or response.status_code == 200 :
        print('The EPC was submitted with success!\n')
    else:
        print('Pos Transaction API Request failed: '+response.text+'\n')