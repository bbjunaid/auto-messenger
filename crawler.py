#!/usr/bin/env python
import json
import re

from bs4 import BeautifulSoup
import calendar
import datetime
import requests
import time

from cookies import get_authentication_cookies
from const import XSRF_COOKIE, LARAVEL_COOKIE, redis_client, CACHE_KEY_MEMBERS
from private_const import BASE_URL, SEARCH_URL, MEMBER_URL, MEMBER_PIC_URL_RE


def main():
    xsrf, laravel = get_authentication_cookies()

    print "XSRF: {xsrf}\n\nLARAVEL: {laravel}".format(xsrf=xsrf, laravel=laravel)

    cookies = {
        XSRF_COOKIE: xsrf,
        LARAVEL_COOKIE: laravel
    }
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }

    if not xsrf or not laravel:
        print "Missing a token"
        return

    print "Crawling through members"
    first = True
    search_url = SEARCH_URL
    members_added = 0

    while(True):
        search_response = requests.get(search_url, headers=headers, cookies=cookies)
        json_data = json.loads(search_response.content)
        members_to_add = json_data['data']['search_results']
        search_url = BASE_URL + json_data['next_page_url']

        if not members_to_add:
            print "Finished crawling"
            break

        if first:
            print "Found {num} members".format(num=json_data['total'])
            first = False

        print "\n\nAdding {num} members in this query. Members added so far {num_so_far}".format(num=len(members_to_add), num_so_far=members_added)
        for member in members_to_add:
            if redis_client.sismember('members-uid', member['uid']):
                continue

            last_logged_in = member['online_status']
            rank = 0
            if last_logged_in not in ['Online', 'Hidden']:
                last_logged_in = last_logged_in[:19]
                try:
                    last_logged_in = calendar.timegm(datetime.datetime.strptime(last_logged_in[:19], '%Y-%m-%dT%H:%M:%S').timetuple())
                    rank = (time.time() - last_logged_in) / 3600
                except:
                    pass

            time.sleep(0.5)
            member_page = requests.get(MEMBER_URL.format(uid=member['uid']), headers=headers, cookies=cookies)
            src_re = re.compile(MEMBER_PIC_URL_RE)
            imgs = BeautifulSoup(member_page.text, 'html.parser').findAll('img', attrs={'src': src_re})
            pics = []
            for img in imgs:
                pics.append(img['src'])
            member_to_add = {
                'uid': member['uid'],
                'username': member['username'],
                'location': member['location'],
                'pics': pics
            }
            redis_client.sadd('members-uid', member['uid'])
            if redis_client.zadd(CACHE_KEY_MEMBERS, rank, member_to_add):
                print u"Adding {username}\t\t{uid} {rank}".format(username=member['username'], uid=member['uid'], rank=round(rank, 4))
                members_added += 1

        time.sleep(1)


if __name__ == "__main__":
    main()
