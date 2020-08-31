import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def gen_hash(password, salt, hash_function):
    digest = hashes.Hash(hash_function, backend=default_backend())
    digest.update(password)
    digest.update(salt)
    return digest.finalize()


def gen_fernet(password, salt, hash_function):
    kdf = PBKDF2HMAC(
        algorithm=hash_function,
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    return f
