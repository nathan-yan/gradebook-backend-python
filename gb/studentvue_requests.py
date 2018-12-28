from . import variables
import requests as r

# Should probably make these the same since they're so similar

def load_quarter(session, control, parameters):
    quarter_html = session.post(variables.BASE_URL + "service/PXP2Communication.asmx/LoadControl", json = {
        "request" : {
            "control" : control,
            "parameters" : parameters
        }
    })

    return quarter_html.json()['d']['Data']['html']

def load_class(session, control, parameters):
    class_html = session.post(variables.BASE_URL + "service/PXP2Communication.asmx/LoadControl", json = {
        "request" : {
            "control" : control,
            "parameters" : parameters
        }
    })

    return class_html.json()['d']['Data']['html']

def load_class_by_cookie(cookie, control, parameters):
    print(cookie)
    class_html = r.post(variables.BASE_URL + "service/PXP2Communication.asmx/LoadControl", cookies = cookie, json = {
        "request" : {
            "control" : control,
            "parameters" : parameters
        }
    })

    return class_html.json()['d']['Data']['html']

"""{
                "schoolID" : "7",
                "OrgYearGU" : "C8636FF0-07E0-4C31-B8D1-17BADE41D7FC",
                "gradePeriodGU" : "1CD9B214-7FEE-41DE-8956-DEEB4C299C6A",
                "GradingPeriodGroup" : "Regular",
                "AGU" : 0
}"""    # just for reference