from flask import Flask, jsonify, request, make_response, redirect

import requests as r
from requests import session 
import time
import json

from bs4 import BeautifulSoup as bs

from .. import variables
from .. import db
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

    print(response_page.text)

    # Do some checking to see if the response_page is correct

    # If the request was valid, log the user into the database
    # If this is a first time login, we register the user by going through the setup

    # Look through all of the classes for their Gradebook_ClassDetails parameters
    # Look through all of the quarters and get their parameters as well
    
    # Also send over the cookies

    test = s.post(variables.BASE_URL + "service/PXP2Communication.asmx/LoadControl", 
    json = {"request" : {
        "control" : "Gradebook_ClassDetails",
        "parameters": {"viewName":None,"studentGU":"AEA18D8C-387E-4CE1-8F05-FE47057D6A61","schoolID":7,"classID":12723,"markPeriodGU":None,"gradePeriodGU":"2F3F407F-596E-46BA-BABF-4BB5B64F0D8B","subjectID":-1,"teacherID":-1,"assignmentID":-1,"standardIdentifier":None,"AGU":"0","OrgYearGU":"C8636FF0-07E0-4CE1-B8D1-17BADE41D7FC"}
    }})

    res = str(test.json()['d']['Data']['html'])
    start_idx = res.index('"dataSource"')
    end_idx = res[start_idx:].index("}]")
    print("{" + res[start_idx:start_idx + end_idx] + "}]}")
    
    class_data = json.loads("{" + res[start_idx:start_idx + end_idx] + "}]}")
    print(class_data['dataSource'][0]['GBAssignment'])

    return json.dumps({
        "status" : "success",
        "cookie" : s.cookies.get_dict()
    })

@api.route("/classes", methods = ['POST'])
def classes():
    print(request.headers['Gb-Cookie'])

    return ""
