import sys
import time
import jwt

"""这里的文件的作用是生成生成JWT的携带的加密访问参数"""

# Open PEM
private_key = """-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIHiS1F6BUJrc1gxAWyWlycqOsQ+0EuKlyv4ARhuRCr9W
-----END PRIVATE KEY-----"""

payload = {
    'iat': int(time.time()) - 30,
    'exp': int(time.time()) + 900,
    'sub': '4E882J92NA'
}
headers = {
    'kid': 'KAGXV3GPU5'
}

# Generate JWT
encoded_jwt = jwt.encode(payload, private_key, algorithm='EdDSA', headers = headers)

print(f"JWT:  {encoded_jwt}")
# curl -H "X-QW-Api-Key: 92648c1ee5eb496782a4048b97aa792d" --compressed \
# 'https://abcxyz.qweatherapi.com/v7/weather/now?location=101010100'