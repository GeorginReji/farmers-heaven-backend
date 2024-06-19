import urllib.parse
import requests
import json

from decouple import config
def send_sms_without_save(phone_no, body):
    requests.get(
        "http://www.smsjust.com/blank/sms/user/urlsms.php?username=whstlr&pass=nsts@123&response=Y&msgtype=UNI&senderid=WHSTLR&dest_mobileno=" + str(
            phone_no) + "&message=" + urllib.parse.quote(str(body)))


def send_sms(phone_no, body):
    res = requests.get(config('SMS_URL'),
                       params={'user': config('SMS_USERNAME'),
                               'pwd': config('SMS_PASSWORD'),
                               'mobileno': phone_no,
                               'text': body,
                               'sender': config('SMS_SENDER_ID'),
                               'response': 'json'})
    return json.loads(res.content)