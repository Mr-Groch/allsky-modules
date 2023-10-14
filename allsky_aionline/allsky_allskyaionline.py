'''
allsky_allskyaionline.py

Part of allsky postprocess.py modules.
https://github.com/thomasjacquin/allsky

This module will retrieve data from the AllSkyAI API

'''
import allsky_shared as s
import os
import requests
import json

metaData = {
    "name": "AllSkyAI Online",
    "description": "Gets results from the AllSkyAI service",
    "module": "allsky_allskyaionline",
    "version": "v1.0.0",
    "experimental": "true",
    "events": [
        "day",
        "night"
    ],
    "arguments":{
        "imageurl": ""
    },
    "argumentdetails": {
        "imageurl": {
            "required": "true",
            "description": "Image public URL",
            "help": "URL of current AllSky image available from internet"
        }
    }
}

def processResult(data):
    #rawData = '{"classification": "precipitation", "confidence": 85.96113920211792, "utc": 1697142569, "inference": 0.04334449768066406, "img": "dKWrFq8v5edHn23JGsFKpF.jpg"}'
    #data = json.loads(rawData)
    os.environ["AS_AICLASSIFICATION"] = data["classification"]
    os.environ["AS_AICONFIDENCE"] = str(data["confidence"])
    os.environ["AS_AIINFERENCE"] = str(data["inference"])

    if (data["classification"] == "clear" or data["classification"] == "light_clouds"):
        os.environ["AS_SKYSTATE"] = "Clear"
    else:
        os.environ["AS_SKYSTATE"] = "NOT Clear"

    if (data["classification"] == "precipitation"):
        os.environ["AS_ALLSKYRAINFLAG"] = "True"
    else:
        os.environ["AS_ALLSKYRAINFLAG"] = "False"

def allskyaionline(params, event):
    result = ""

    imageurl = params["imageurl"]

    if imageurl != "":
        allskyPath = s.getEnvironmentVariable("ALLSKY_HOME")
        if allskyPath is not None:
            try:
                resultURL = "https://allskyai.com/tfapi/v1/live?url={}".format(imageurl)
                response = requests.get(resultURL)
                if response.status_code == 200:
                    rawData = response.json()
                    processResult(rawData)
                    result = "Data acquired, classification: {}".format(rawData["classification"])
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

    return result

def allskyaionline_cleanup():
    moduleData = {
        "metaData": metaData,
        "cleanup": {
            "files": {},
            "env": {
                "AS_SKYSTATE",
                "AS_ALLSKYRAINFLAG",
                "AS_AICLASSIFICATION",
                "AS_AICONFIDENCE",
                "AS_AIINFERENCE"
            }
        }
    }
    s.cleanupModule(moduleData)
