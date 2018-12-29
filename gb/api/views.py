from flask import Flask, jsonify, request, make_response, redirect

import requests as r
from requests import session 
import time
import json

from bs4 import BeautifulSoup as bs

from .. import db
from .. import auth
from .. import variables
from .. import exceptions
from .. import studentvue_requests

from . import api

from flask_cors import CORS

@api.route("/authenticate", methods = ["POST"])
def authenticate():
    username = request.form.get("username")
    password = request.form.get("password")

    # Request the StudentVue login page
    s = session()
    login_page = s.get(variables.BASE_URL + "PXP2_Login_Student.aspx?regenerateSessionId=True")
    parsed_login_page = bs(login_page.text)
    print('got gb page')

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

  #  print(response_page.text)

    # Do some checking to see if the response_page is correct

    # If the request was valid, log the user into the database
    # If this is a first time login, we register the user by going through the setup

    # Look through all of the classes for their Gradebook_ClassDetails parameters
    # Look through all of the quarters and get their parameters as well
    
    # Also send over the cookies

    # Put token and username in db
    user = db.USERS.find_one({
        "username" : username
    })

    print('found user')

    token = auth.generate_token()

    if (not user):  # User does not exist, do some initialization stuff and insert the user into the db with the initialized flag set to false
        gradebook_page = s.get(variables.BASE_URL + "PXP2_Gradebook.aspx?AGU=0")

        # Get all arguments for each 

        parsed_gradebook_page = bs(gradebook_page.text)

        # First get the PXP.AGU
        agu = 0
        div = parsed_gradebook_page.find("div", attrs = {
            "class" : "update-panel"
        })

        school_id = div.attrs.get('data-school-id')
        org_year = div.attrs.get('data-orgyear-id')

        # Get quarter information
        dropdown_quarters = parsed_gradebook_page.find("ul", attrs = {
            "class" : "dropdown-menu",
            "role" : "menu"
        })

        dropdown_quarters_links = dropdown_quarters.find_all("a")
        quarter_args = []
        for link in dropdown_quarters_links:
            args = {
                "periodGroup" : link.attrs['data-period-group'],
                "periodId" : link.attrs['data-period-id']
            }

            quarter_args.append(args)

        class_args = []

        for quarter in quarter_args:
            parsed_quarter = bs(studentvue_requests.load_quarter(s, "Gradebook_SchoolClasses", {
                "schoolID" : 7,
                "OrgYearGU" : org_year,
                "gradePeriodGU" : quarter["periodId"],
                "GradingPeriodGroup" : quarter["periodGroup"],
                "AGU" : 0
            }))

            # Get class information
            table = parsed_quarter.find("table", attrs = {
                "class" : "data-table"
            })

            classes = table.find_all('tr')
            
            args = {}
            for c in classes[1:]:
                args_ = c.find('button', attrs = {  # my variable naming is not so great, better change this in the future. args_ is the arguments for a specific class of a quarter, while args (without underscore) is the arguments for all classes of a quarter
                    "data-action" : "GB.LoadControl"
                })

                period = c.find('td', attrs = {
                    "class" : "period"
                }).get_text()

                args[period] = json.loads(args_.attrs.get("data-focus"))   # Make sure to change gradePeriodGU when getting classes of different quarters

            class_args.append(args)

        # Get current quarter
        current_quarter_arg = parsed_page.find("button", attrs = {
            "class" : "btn-link"
        }).attrs.get("data-term-name")

        for (q, quarter) in enumerate(user['classArgs']):
            print(quarter)
            if quarter[quarter.keys()[0]]['FocusArgs']['gradePeriodGU'] == current_quarter_arg:
                current_quarter = q
                break;

        db.USERS.insert_one({
            "username" : username,
            "initialized" : True,
            "studentVueMeta" : {
                "schoolId" : school_id,
                "orgYear" : org_year
            },
            "classArgs" : class_args,
            "quarterArgs" : quarter_args,
            "currentQuarterArg" : "",
            "profile" : "",
            "synergyCookies" : s.cookies.get_dict(),
            "currentQuarter" : current_quarter
        })

    else:
        print('in else')
        db.USERS.update_one({
            "username" : username
        }, {
            "$set" : {
                "synergyCookies" : s.cookies.get_dict()
            }
        }, upsert = False)

        db.SESSIONS.insert_one({
            "username" : username,
            "token" : token,
            "time_created" : time.time()            # there is a mongodb thing for automatically deleting these, don't remember how to do it though, will have to settle for this for now
        })

    # Set GradeBook cookies

    response = make_response(json.dumps({
        "you are" : "logged in!"
    }))

    response.set_cookie("token", token, httponly = True)
    response.set_cookie("username", username, httponly = True)

    return response

@api.route("/classes", methods = ['GET'])
def classes():
    try:
        verified = auth.auth_by_cookie(request)
    except exceptions.InvalidCookiesError:
        return json.dumps({
            "status" : "failed",
            "error_reason" : "INVALID_COOKIES_GB"
        }), 401
    except exceptions.InvalidAPIKeyError:
        return json.dumps({
            "status" : "failed",
            "error_reason" : "INVALID_API_KEY"
        })
    
    username, cookies = verified
    user = db.USERS.find_one({
        "username" : username
    })

    if not user:
        return json.dumps({
            "status" : "failed",
            "error_reason" : "NO_ACCOUNT"
        }), 403

    classes_page = r.get(variables.BASE_URL + "/PXP2_Gradebook.aspx?AGU=0", cookies = user['synergyCookies'])

   # print(classes_page.text)

    parsed_page = bs(classes_page.text)
    table = parsed_page.find("table", attrs = {
        "class" : "data-table"
    })

    classes = table.find_all('tr')
    
    class_data = []

    current_quarter_arg = parsed_page.find("button", attrs = {
        "class" : "btn-link"
    }).attrs.get("data-term-name")

    for (q, quarter) in enumerate(user['classArgs']):
        print(quarter)
        if quarter[quarter.keys()[0]]['FocusArgs']['gradePeriodGU'] == current_quarter_arg:
            current_quarter = q
            break;

    db.USERS.update_one({
        "_id" : user['_id']
    }, {
        "$set" : {
            "currentQuarter" : current_quarter
        }
    })

    for c in classes[1:]:
        period = c.find("td", attrs = {
            "class" : "period"
        }).get_text()

        class_name = c.find("button", attrs = {
            "class" : "course-title"
        }).get_text()

        teacher_name = c.find("span", attrs = {
            "class" : "teacher"
        }).get_text()

        room = c.find("div", attrs = {
            "class" : "teacher-room"
        }).get_text()

        grade = c.find("span", attrs = {
            "class" : "score"
        }).get_text()

        class_data.append({
            "teacher" : teacher_name,
            "class_name" : class_name,
            "grade" : grade, 
            "period" : period,
            "room" : room
        })

    return json.dumps({
        "data" : class_data
    })

@api.route("/classes/<period>", methods = ['GET'])
def class_period(period):
    try:
        verified = auth.auth_by_cookie(request)
    except exceptions.InvalidCookiesError:
        return json.dumps({
            "status" : "failed",
            "error_reason" : "INVALID_COOKIES_GB"
        }), 401
    except exceptions.InvalidAPIKeyError:
        return json.dumps({
            "status" : "failed",
            "error_reason" : "INVALID_API_KEY"
        })
    
    username, cookies = verified

    user = db.USERS.find_one({
        "username" : username
    })

    if not user:
        return json.dumps({
            "status" : "failed",
            "error_reason" : "NO_ACCOUNT"
        }), 403

    quarter = user['currentQuarter']
    class_information = studentvue_requests.load_class_by_cookie(user['synergyCookies'], "Gradebook_ClassDetails", 
        user['classArgs'][quarter][period]['FocusArgs'] #this is a fat yikes
    )

    # Get category weightings
    categories = {}

    try:
        start_idx = class_information.index("data-data-source=")
        end_idx = class_information.index('>', start_idx)

        # The +1 and -1 are to take out the quotation marks at the beginning
        category_data = json.loads(class_information[start_idx + len("data-data-source=") + 1 : end_idx - 1].replace("&quot;", '"'))

        for category in category_data:
            categories[category.get("Category")] = {
                "percentage" : float(category.get("PctOfGrade")) 
            }

    except ValueError:
        pass


    start_idx = class_information.index('"dataSource"')
    end_idx = class_information[start_idx:].index("}]")

    assignment_data = json.loads("{" + class_information[start_idx : start_idx + end_idx] + "}]}")
    #print(class_data['dataSource'][0])

    print(assignment_data)

    assignments = []

    for assignment in assignment_data['dataSource']:
        category = assignment['GBAssignmentType']
        points = assignment['GBPoints'] # Gotta do some processing on this, not all assignments have a score assigned to them
        comments = bs(assignment['GBNotes']).get_text()    # StudentVUE directly stores their HTML in this so we need to parse it with beautifulSoup then extract the text from this (ugh)
        name = json.loads(assignment['GBAssignment'])['value']
        date = assignment['Date']

        if '/' in points:
            pointsEarned, pointsTotal = points.split('/')
            pointsEarned, pointsTotal = float(pointsEarned), float(pointsTotal)
        else:
            pointsEarned = 'NA'
            pointsTotal = 'NA'

        assignments.append({
            "name" : name,
            "category" : category,
            "pointsEarned" : pointsEarned,
            "pointsTotal" : pointsTotal,
            "comments" : comments, 
            "date" : date
        })

    return json.dumps({
        "categories" : categories,
        "assignments" : assignments 
    })

"""test = s.post(variables.BASE_URL + "service/PXP2Communication.asmx/LoadControl", 
    json = {"request" : {
        "control" : "Gradebook_ClassDetails",
        "parameters": {"viewName":None,"studentGU":"AEA18D8C-387E-4CE1-8F05-FE47057D6A61","schoolID":7,"classID":12723,"markPeriodGU":None,"gradePeriodGU":"2F3F407F-596E-46BA-BABF-4BB5B64F0D8B","subjectID":-1,"teacherID":-1,"assignmentID":-1,"standardIdentifier":None,"AGU":"0","OrgYearGU":"C8636FF0-07E0-4CE1-B8D1-17BADE41D7FC"}
    }})

    another_test = s.post(variables.BASE_URL + "service/PXP2Communication.asmx/LoadControl", json = {
        "request" : {
            "control" : "Gradebook_SchoolClasses",
            "parameters" : {
                "schoolID" : "7",
                "OrgYearGU" : "C8636FF0-07E0-4C31-B8D1-17BADE41D7FC",
                "gradePeriodGU" : "1CD9B214-7FEE-41DE-8956-DEEB4C299C6A",
                "GradingPeriodGroup" : "Regular",
                "AGU" : 0
            }
        }
    })

    print(another_test.text)

    res = str(test.json()['d']['Data']['html'])
    start_idx = res.index('"dataSource"')
    end_idx = res[start_idx:].index("}]")
    #print("{" + res[start_idx:start_idx + end_idx] + "}]}")
    
    class_data = json.loads("{" + res[start_idx:start_idx + end_idx] + "}]}")
    #print(class_data['dataSource'][0]['GBAssignment'])"""

@api.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'

    return response