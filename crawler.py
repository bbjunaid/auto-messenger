#!/usr/bin/env python
import calendar
import datetime
import json
import re
import time

from bs4 import BeautifulSoup
import requests

from cookies import get_authentication_cookies
from const import XSRF_COOKIE, LARAVEL_COOKIE, redis_client, CACHE_KEY_LAST_SEARCH, COOKIES, HEADERS
from models import MemberModel
from private_const import BASE_URL, SEARCH_URL, MEMBER_URL, MEMBER_PIC_URL_RE, MEMBER_MSG_URL_RE, MEMBER_CONVO_URL_RE, MY_PHONE


def main():
    print "Starting"
    xsrf, laravel = get_authentication_cookies()

    print "XSRF: {xsrf}\n\nLARAVEL: {laravel}".format(xsrf=xsrf, laravel=laravel)

    COOKIES[XSRF_COOKIE] = xsrf
    COOKIES[LARAVEL_COOKIE] = laravel

    if not xsrf or not laravel:
        print "Missing a token"
        return

    print "Crawling through members"
    first = True
    search_url = SEARCH_URL
    members_added = 0

    while(True):
        search_response = requests.get(search_url, headers=HEADERS, cookies=COOKIES)
        json_data = json.loads(search_response.content)
        members_to_add = json_data['data']['search_results']

        if not members_to_add:
            print "Finished crawling"
            break

        search_url = BASE_URL + json_data['next_page_url']

        if not members_to_add:
            print "Finished crawling"
            break

        if first:
            print "Found {num} members".format(num=json_data['total'])
            first = False

        print "\n\nAdding {num} members in this query.".format(num=len(members_to_add))
        for member in members_to_add:
            time.sleep(0.5)

            last_logged_in, logged_in_string = _get_time_stamp_and_string(member['online_status'])

            try:
                member_to_add = MemberModel.get(member['uid'])
                if member_to_add:
                    three_hours = 24*60*60
                    has_time_elapsed = (time.time() - member_to_add.last_full_updated) > three_hours

                    if not has_time_elapsed:
                        output = u"Not updating {uid} {username} yet".format(uid=member['uid'], username=member['username'])
                        print output.encode('utf-8')
                        member_to_add.last_logged_in_stamp = last_logged_in
                        member_to_add.last_logged_in = logged_in_string
                        member_to_add.save()
                        continue
            except:
                output = "Didn't find {uid} {username} in database".format(uid=member['uid'], username=member['username'])
                print output.encode('utf-8')
                pass

            member_page = requests.get(MEMBER_URL.format(uid=member['uid']), headers=HEADERS, cookies=COOKIES)
            pics, msgs, phone = [], [], ''

            try:
                pics = _get_member_imgs(member_page)
                msgs, phone = _get_msgs_and_phone(member_page)
            except Exception as e:
                print e.message

            output = u"Adding {uid} {username}".format(uid=member['uid'], username=member['username'])
            print output.encode('utf-8')
            member_to_add = MemberModel(member['uid'],
                                        last_logged_in_stamp=last_logged_in,
                                        last_logged_in=logged_in_string,
                                        username=member['username'],
                                        location=member['location'],
                                        pics=pics,
                                        msgs=msgs,
                                        phone=phone,
                                        last_full_updated=time.time())
            member_to_add.save()

        time.sleep(1)


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


def _get_member_imgs(member_page):
    member_page_bs = BeautifulSoup(member_page.text, 'html.parser')
    src_re = re.compile(MEMBER_PIC_URL_RE)
    imgs = member_page_bs.findAll('img', attrs={'src': src_re})
    pics = []
    for img in imgs:
        pics.append(img['src'])

    return pics


def _get_msgs_and_phone(member_page):
    member_page_bs = BeautifulSoup(member_page.text, 'html.parser')
    msg_re = re.compile(MEMBER_MSG_URL_RE)
    msg_url = member_page_bs.find('a', attrs={'href': msg_re})['href']

    msgs_page = requests.get(msg_url, cookies=COOKIES, headers=HEADERS)
    m = re.search(r".*var conversationId = (\d+);.*", msgs_page.text)
    convo_id = m.group(1)
    msgs = []
    phone = ''

    if convo_id == '0':
        return msgs, phone

    convo = requests.get(MEMBER_CONVO_URL_RE.format(convo_id=convo_id), cookies=COOKIES, headers=HEADERS)
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
    phone = ''
    for s in msg:
        if s.isdigit():
            phone += s
    length = len(phone)
    if length >= 10:
        if length > 10:
            phone = phone[length-10:]
        if phone != MY_PHONE:
            pretty_phone = '{first}-{second}-{third}'.format(first=phone[:3], second=phone[3:6], third=phone[6:])
            return pretty_phone
    return ''


if __name__ == "__main__":
    main()
