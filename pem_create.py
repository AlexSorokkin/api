import time
import jwt
import requests
from jwt.algorithms import RSAAlgorithm
# ajenl8v0h30nqktgu9gh
# ajevhga6oa34n10mm42g

service_account_id = "ajenl8v0h30nqktgu9gh"
key_id = "ajevhga6oa34n10mm42g"  # ID ресурса Key, который принадлежит сервисному аккаунту.

with open("private.pem", 'r') as private:
    private_key = private.read() # Чтение закрытого ключа из файла.
now = int(time.time())
payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 360}


# Формирование JWT.
encoded_token = jwt.encode(
    payload,
    private_key,
    algorithm='PS256',
    headers={'kid': key_id})


zapr = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'

params = {'jwt': encoded_token}

response = requests.post(zapr, params=params)

print(response.json())