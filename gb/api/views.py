from flask import Flask, jsonify, request, make_response, redirect

import requests as r
from requests import session 
import time
import json

from bs4 import BeautifulSoup as bs

from .. import variables
from . import api

@api.route("/authenticate", methods = ["POST"])
def authenticate():
    username = request.form.get("username")
    password = request.form.get("password")

    # Request the StudentVue login page
    s = session()
    login_page = s.get(variables.BASE_URL + "PXP2_Login_Student.aspx?regenerateSessionId=True")
    parsed_login_page = bs(login_page.text)

    cookies = login_page.cookies.get_dict()

    inputs = parsed_login_page.find_all("input")

    # Generate a payload with the proper inputs filled out
    authentication_payload = {}

    for inp in inputs:
        name = inp.attrs.get('name')
        value = inp.attrs.get('value')

        authentication_payload[name] = value

    # Inject the username and password into the authentication paylaod
    authentication_payload['ctl00$MainContent$username'] = username
    authentication_payload['ctl00$MainContent$password'] = password

    # Send the payload
    response_page = s.post(variables.BASE_URL + "PXP2_Login_Student.aspx?regenerateSessionId=True", authentication_payload)

    # Do some checking to see if the response_page is correct

    # If the request was valid, send over the cookies
    print(s.cookies)

    return json.dumps({
        "status" : "success",
        "cookie" : s.cookies.get_dict()
    })