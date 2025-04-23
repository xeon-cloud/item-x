from . import config
import requests

def renderAuthUrl():
    return f'https://oauth.yandex.ru/authorize?response_type=code&client_id={config.YA_CLIENT_ID}&redirect_uri={config.REDIRECT_URL}&scope=login:email'

def getAccessToken(code: str):
    url = 'https://oauth.yandex.ru/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': config.YA_CLIENT_ID,
        'client_secret': config.YA_SECRET,
        'redirect_uri': config.REDIRECT_URL
    }
    response = requests.post(url, data=data)
    return response.json()['access_token']

def authorizeUser(code: str):
    accessToken = getAccessToken(code)
    url = 'https://login.yandex.ru/info'
    params = {
        'format': 'json',
        'oauth_token': accessToken,
        'fields': 'id,first_name,last_name,email,default_avatar_id'
    }
    response = requests.get(url, params=params)
    return response.json()