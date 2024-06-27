import json
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
#from dotenv import load_dotenv

#load_dotenv()

SECRET_SALT = os.getenv('SECRET_SALT', 'Secret Salt You Should Update')
SECRET_PASSPHRASE = os.getenv('SECRET_PASSPHRASE', 'Secret Key You Should Update')

print(f"Using salt: {SECRET_SALT}")
print(f"Using passphrase: {SECRET_PASSPHRASE}")

# Derive key from passphrase and salt
def derive_key(passphrase, salt):
    kdf = Scrypt(
        salt=salt.encode(),
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key = kdf.derive(passphrase.encode())
    return key

secret_key = derive_key(SECRET_PASSPHRASE, SECRET_SALT)

def encrypt_string(input_string, key=secret_key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    plaintext = input_string.encode('utf-8')
    encrypted = encryptor.update(plaintext) + encryptor.finalize()
    auth_tag = encryptor.tag

    result = {
        'iv': iv.hex(),
        'auth_tag': auth_tag.hex(),
        'data': encrypted.hex(),
    }
    # print(json.dumps(result))
    return json.dumps(result)

def decrypt_string(input_string, key=secret_key):
    encrypted_data = json.loads(input_string)

    iv = bytes.fromhex(encrypted_data['iv'])
    auth_tag = bytes.fromhex(encrypted_data['auth_tag'])
    ciphertext = bytes.fromhex(encrypted_data['data'])

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, auth_tag), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted = decryptor.update(ciphertext) + decryptor.finalize()
    print(decrypted.decode('utf-8'))
    return decrypted.decode('utf-8')

# Encrypt file
def encrypt_file(input_path, key=secret_key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(input_path, 'r') as f:
        plaintext = f.read().encode('utf-8')

    encrypted = encryptor.update(plaintext) + encryptor.finalize()
    auth_tag = encryptor.tag

    result = {
        'iv': iv.hex(),
        'auth_tag': auth_tag.hex(),
        'data': encrypted.hex(),
    }

    with open(f"{input_path}.secure", 'w') as f:
        json.dump(result, f)

    print(f"Encrypted file written to {input_path}.secure!")

# Decrypt file
def decrypt_to_string(input_path, key=secret_key):
    print(f"Decrypting {input_path}...")
    with open(input_path, 'r') as f:
        encrypted_data = json.load(f)

    iv = bytes.fromhex(encrypted_data['iv'])
    auth_tag = bytes.fromhex(encrypted_data['auth_tag'])
    ciphertext = bytes.fromhex(encrypted_data['data'])

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, auth_tag), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted.decode('utf-8')

# Example usage:
# encrypt_file('test.txt')
# decrypted_message = decrypt_to_string('test.txt.secure')
# print(decrypted_message)

if __name__ == "__main__":
    # Encrypt a test file
    encrypt_file('serviceAccount.json')
    # Decrypt the file and print the result
    decrypted_message = decrypt_to_string('serviceAccount.json.secure')
    print(decrypted_message)
