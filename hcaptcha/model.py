from . import config
import requests

def validateCaptcha(token):
    response = requests.post('https://hcaptcha.com/siteverify', data={'secret': config.SECRET_KEY,
                                                                      'response': token})
    return response.json().get('success')