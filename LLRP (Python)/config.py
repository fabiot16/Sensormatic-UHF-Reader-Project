
api_config_stg = {
    'username':'esp32-staging-pos',
    'password':'Tyco1234!',
    'auth_api_url':'https://auth.sea.stg.cloud.sensormatic.com/realms/sensormatic/protocol/openid-connect/token',
    'api_url':'https://sea.stg.cloud.sensormatic.com' 
}

auth_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

auth_login_body = 'client_id=smartexit-api&grant_type=password&username={}&password={}'.format(api_config_stg['username'],api_config_stg['password'])


