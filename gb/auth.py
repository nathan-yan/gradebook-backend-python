import os

from . import db
from . import exceptions

# If we're using Python 3.6 or above we should use secrets
def generate_token(length = 16):
    random_bytes = os.urandom(length)

    valid_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'

    res = ""
    for byte in random_bytes:
        res += valid_characters[byte % len(valid_characters)]

    return res

    # return secrets.token_urlsafe(length)

def check_api_key(request):
    headers = request.headers


def auth_by_cookie(request):
    cookies = request.cookies

    username, token = cookies.get('username'), cookies.get('token')

    session = db.SESSIONS.find_one({
        "username": username,
        "token" : token
    })

    # Do timestamp checking here

    if session:
        return username, token 
    else:
        raise exceptions.InvalidCookiesError("Invalid Cookies. USERNAME = %s, TOKEN = %s" % (username, token))
    
