#!/usr/bin/env python
import json

import requests
import time

from cookies import get_authentication_cookies
from const import XSRF_COOKIE, LARAVEL_COOKIE, redis_client, CACHE_KEY_MEMBERS
from private_const import BASE_URL, SEARCH_URL


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

        if not members_to_add or members_added > 150:
            print "Finished crawling"
            break

        if first:
            print "Found {num} members".format(num=json_data['total'])
            first = False

        print "\n\nAdding {num} members in this query".format(num=len(members_to_add))
        for member in members_to_add:
            if redis_client.sadd(CACHE_KEY_MEMBERS, member['uid']):
                print u"Adding {username}\t\t{uid}".format(username=member['username'], uid=member['uid'])
                members_added += 1

        time.sleep(2)


if __name__ == "__main__":
    main()
