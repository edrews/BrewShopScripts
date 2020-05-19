#!/usr/bin/env python3
import json
import requests
import time
from datetime import datetime, timedelta

KEY_URL = "https://www.arlbrew.com/api/form/FormSubmissionKey"
SUBMIT_URL = "https://www.arlbrew.com/api/form/SaveFormSubmission"

HEADERS ={
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.arlbrew.com",
    "referer": "https://www.arlbrew.com/pickupanddelivery",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "x-csrf-token": "undefined",
}

SUBMIT_DATA = {
    "key": "CHANGE_ME",
    "formId": "5e6ff1f28a838c0e13701a8e",
    "collectionId": "5e6ff1f28a838c0e13701a90",
    "objectName": "page-5e6ff1f28a838c0e13701a90",
    "form": "{ \
\"name-yui_3_17_2_1_1543962691214_44998\":[\"Canary\",\"Test\"], \
\"email-yui_3_17_2_1_1543962691214_44999\":\"CanaryTest@gmail.com\", \
\"phone-yui_3_17_2_1_1543962568663_24016\":[\"\",\"111\",\"111\",\"1111\"], \
\"address-yui_3_17_2_1_1584394717221_33892\":[\"CanaryTest\",\"CanaryTest\",\"CanaryTest\",\"CanaryTest\",\"CanaryTest\",\"CanaryTest\"], \
\"date-yui_3_17_2_1_1584394717221_34606\":[\"11\",\"11\",\"1111\"], \
\"select-yui_3_17_2_1_1584394717221_36302\":\"Curbside Pick-Up ($25 Minimum)\", \
\"select-yui_3_17_2_1_1585398245792_24813\":\"In Advance (Over the Phone)\", \
\"textarea-yui_3_17_2_1_1584394717221_35348\":\"CanaryTest\" \
}",
    "pageTitle": "Curbside Pick-Up and Delivery",
    "pageId": "5e6ff1f28a838c0e13701a90",
    "contentSource": "c",
    "pagePath": "/pickupanddelivery",
}

def submit_form():
    key_response = requests.post(url = KEY_URL, headers = HEADERS) 
    SUBMIT_DATA['key'] = key_response.json()['key']
    submit_response = requests.post(url = SUBMIT_URL, headers = HEADERS, data = json.dumps(SUBMIT_DATA)) 

def run_job():
    while 1:
        print("Waiting for top of the hour...")
        dt = datetime.now() + timedelta(hours=1)
        dt = dt.replace(minute=0, second=0)
        while datetime.now() < dt:
            time.sleep(1)
        print("Submitting web form...")
        submit_form()

if __name__ == "__main__":
    run_job()
