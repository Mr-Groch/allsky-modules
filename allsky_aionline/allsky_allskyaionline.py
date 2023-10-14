'''
allsky_allskyaionline.py

Part of allsky postprocess.py modules.
https://github.com/thomasjacquin/allsky

This module will retrieve data from the AllSkyAI API

'''
import allsky_shared as s
import requests
import json

metaData = {
    "name": "AllSkyAI Online",
    "description": "Gets results from the AllSkyAI service",
    "module": "allsky_allskyaionline",
    "version": "v1.0.0",
    "events": [
        "day",
        "night"
    ],
    "arguments":{
        "period": 60,
        "expire": 240,
        "filename": "allskyai.json",
        "imageurl": ""
    },
    "argumentdetails": {
        "imageurl": {
            "required": "true",
            "description": "Image public URL",
            "help": "URL of current AllSky image available from internet"
        },
        "filename": {
            "required": "true",
            "description": "Filename",
            "help": "The name of the file that will be written to the allsky/tmp/extra directory"
        },
        "period" : {
            "required": "true",
            "description": "Read Every",
            "help": "Reads data every x seconds",
            "type": {
                "fieldtype": "spinner",
                "min": 30,
                "max": 1440,
                "step": 1
            }
        },
        "expire" : {
            "required": "true",
            "description": "Expiry Time",
            "help": "Number of seconds the data is valid for MUST be higher than the 'Read Every' value",
            "type": {
                "fieldtype": "spinner",
                "min": 31,
                "max": 1500,
                "step": 1
            }
        }
    }
}

extraData = {}

def processResult(data, expires):
    #rawData = '{"classification": "precipitation", "confidence": 85.96113920211792, "utc": 1697142569, "inference": 0.04334449768066406, "img": "dKWrFq8v5edHn23JGsFKpF.jpg"}'
    #data = json.loads(rawData)
    setExtraValue(data["classification"], "AICLASSIFICATION", expires)
    setExtraValue(data["confidence"], "AICONFIDENCE", expires)
    setExtraValue(data["inference"], "AIINFERENCE", expires)

    if (data["classification"] == "clear" or data["classification"] == "light_clouds"):
        setExtraValue("Clear", "SKYSTATE", expires)
    else:
        setExtraValue("NOT Clear", "SKYSTATE", expires)

    if (data["classification"] == "precipitation"):
        setExtraValue("True", "ALLSKYRAINFLAG", expires)
    else:
        setExtraValue("False", "ALLSKYRAINFLAG", expires)

def setExtraValue(value, extraKey, expires):
    global extraData
    if value is not None:
        extraData["AS_" + extraKey] = {
            "value": value,
            "expires": expires
        }

def allskyaionline(params, event):
    global extraData
    result = ""

    expire = int(params["expire"])
    period = int(params["period"])
    fileName = params["filename"]
    imageurl = params["imageurl"]
    module = metaData["module"]

    shouldRun, diff = s.shouldRun(module, period)
    if shouldRun:
        if fileName != "":
            if imageurl != "":
                allskyPath = s.getEnvironmentVariable("ALLSKY_HOME")
                if allskyPath is not None:
                    try:
                        resultURL = "https://allskyai.com/tfapi/v1/live?url={}".format(imageurl)
                        response = requests.get(resultURL)
                        if response.status_code == 200:
                            rawData = response.json()
                            processResult(rawData, expire)
                            s.saveExtraData(fileName, extraData)
                            result = "Data acquired and written to extra data file {}. Classification: {}".format(fileName, rawData["classification"])
                            s.log(1,"INFO: {}".format(result))
                        else:
                            result = "Got error from AllSkyAI API. Response code {}".format(response.status_code)
                            s.log(0,"ERROR: {}".format(result))
                    except Exception as e:
                        result = str(e)
                        s.log(0, "ERROR: {}".format(result))
                else:
                    result = "Cannot find ALLSKY_HOME Environment variable"
                    s.log(0,"ERROR: {}".format(result))
            else:
                result = "Missing public image url"
                s.log(0,"ERROR: {}".format(result))
        else:
            result = "Missing filename for data"
            s.log(0,"ERROR: {}".format(result))

        s.setLastRun(module)
    else:
        result = "Last run {} seconds ago. Running every {} seconds".format(diff, period)
        s.log(1,"INFO: {}".format(result))

    return result

def allskyaionline_cleanup():
    moduleData = {
        "metaData": metaData,
        "cleanup": {
            "files": {
                "allskyai.json"
            },
            "env": {
                "AS_SKYSTATE",
                "AS_ALLSKYRAINFLAG"
            }
        }
    }
    s.cleanupModule(moduleData)
