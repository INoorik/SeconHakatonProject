from yandexid import *

yandex_oauth = YandexOAuth(
    client_id='b8896b95d4e4486c98f09dedce538379',
    client_secret='106fbd36a6e04b4cb2eecddb2281c59c',
    redirect_uri='http://127.0.0.1:5000/login'
)
auth_url = yandex_oauth.get_authorization_url()
print(auth_url)