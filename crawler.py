#!/usr/bin/env python
import json
import re
import time

from bs4 import BeautifulSoup
import requests

from cookies import get_authentication_cookies
from const import XSRF_COOKIE, LARAVEL_COOKIE, COOKIES, HEADERS
from helpers import _get_time_stamp_and_string, _get_msgs_and_phone, _print
from models import MemberModel
from private_const import BASE_URL, SEARCH_URL, MEMBER_URL, MEMBER_PIC_URL_RE


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
                    one_week = 7*24*60*60
                    has_time_elapsed = (time.time() - member_to_add.last_full_updated) > one_week

                    if not has_time_elapsed:
                        _print(u"Not updating {uid} {username} yet".format(uid=member['uid'], username=member['username']))
                        member_to_add.last_logged_in_stamp = last_logged_in
                        member_to_add.last_logged_in = logged_in_string
                        member_to_add.save()
                        continue
            except:
                _print(u"Didn't find {uid} {username} in database".format(uid=member['uid'], username=member['username']))
                pass

            member_page = requests.get(MEMBER_URL.format(uid=member['uid']), headers=HEADERS, cookies=COOKIES)
            pics, msgs, phone = [], [], ''

            try:
                pics = _get_member_imgs(member_page)
                msgs, phone = _get_msgs_and_phone(member['uid'])
            except Exception as e:
                print e.message

            _print(u"Adding {uid} {username}".format(uid=member['uid'], username=member['username']))
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


def _get_member_imgs(member_page):
    member_page_bs = BeautifulSoup(member_page.text, 'html.parser')
    src_re = re.compile(MEMBER_PIC_URL_RE)
    imgs = member_page_bs.findAll('img', attrs={'src': src_re})
    pics = []
    for img in imgs:
        pics.append(img['src'])

    return pics


if __name__ == "__main__":
    main()
