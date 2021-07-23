import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from base64 import b64decode, b64encode

backend = default_backend()


def encrypt(data, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    data_text = json.dumps(data).encode('utf-8')
    padder = padding.PKCS7(128).padder()
    data_res = padder.update(data_text) + padder.finalize()

    cipher = encryptor.update(data_res) + encryptor.finalize()
    return b64encode(cipher).decode('utf-8')


def decrypt(data, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    data = b64decode(data.content)
    unpadder = padding.PKCS7(128).unpadder()
    plain = decryptor.update(data) + decryptor.finalize()
    plain = unpadder.update(plain) + unpadder.finalize()
    return plain.decode('utf-8')


if __name__ == '__main__':
    data = 'test'
    key = iv = b'WLMjHQ7RAOqpzztV'
    data = encrypt(data, key, iv)
    print(data)
    print(decrypt(data, key, iv))
