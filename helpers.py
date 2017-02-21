import calendar
import datetime
import json
import re
import time

import phonenumbers
import requests

from private_const import MEMBER_MSG_URL, MEMBER_CONVO_URL, MY_PHONE
from const import COOKIES, HEADERS, XSRF_COOKIE
from cookies import populate_cookies_dict


def _get_msgs_and_phone(member_uid):
    if COOKIES[XSRF_COOKIE] == '':
        populate_cookies_dict(COOKIES)

    msgs = []
    phone = ''

    msgs_page = requests.get(MEMBER_MSG_URL.format(uid=member_uid), cookies=COOKIES, headers=HEADERS)
    m = re.search('var conversationId = (\d+);', msgs_page.content)
    convo_id = m.group(1)

    if int(convo_id) == 0:
        return msgs, phone

    convo = requests.get(MEMBER_CONVO_URL.format(convo_id=convo_id), cookies=COOKIES, headers=HEADERS)
    convo_data = json.loads(convo.content)

    for msg in convo_data:
        _, string = _get_time_stamp_and_string(msg['created_at'])
        msg_item = {
            'username': msg['author']['username'],
            'msg': msg['body'],
            'created_at': string
        }
        msgs.append(msg_item)
        if not phone:
            phone = _parse_phone(msg['body'])

    return msgs, phone


def _parse_phone(msg):
    for match in phonenumbers.PhoneNumberMatcher(msg, "US"):
        number = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        if number != MY_PHONE:
            return number
    return ''


def _get_time_stamp_and_string(last_logged_in):
    string = last_logged_in
    if last_logged_in in ['Online', 'Hidden']:
        last_logged_in = time.time()
    else:
        last_logged_in = last_logged_in[:19]
        string = last_logged_in
        try:
            last_logged_in = calendar.timegm(datetime.datetime.strptime(last_logged_in[:19], '%Y-%m-%dT%H:%M:%S').timetuple())
        except:
            last_logged_in = time.time()
            pass
    return last_logged_in, string


def _print(msg):
    print msg.encode('utf-8')
