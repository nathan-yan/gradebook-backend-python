import os

# If we're using Python 3.6 or above we should use secrets
def generate_token(length = 16):
    random_bytes = os.urandom(length)

    valid_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'

    res = ""
    for byte in random_bytes:
        res += valid_characters[ord(byte) % len(valid_characters)]

    return res

    # return secrets.token_urlsafe(length)

