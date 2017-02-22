import requests
import json
import time
from const import COOKIES, HEADERS
from cookies import populate_cookies_dict
from private_const import UNREAD_URL, BASE_URL
from helpers import _get_msgs_and_phone, _print
from messenger import _state_machine, _state_machine_action
from models import MemberModel


def main():
    print "Starting replier"
    populate_cookies_dict(COOKIES)

    url = UNREAD_URL
    unread_count = 0
    first = True
    while True and url:
        unread = requests.get(url, headers=HEADERS, cookies=COOKIES)
        data = json.loads(unread.content)
        url = BASE_URL + data['next_page_url'] if data['next_page_url'] else ''
        msgs = data['data']

        if first:
            print "Total unread: {unread}".format(unread=data['unread_inbox_count'])
            first = False

        unread_count += len(msgs)

        for msg in msgs:
            time.sleep(1)
            member_uid = msg['last_message']['author']['uid']
            username = msg['participants'][0]['username']
            try:
                print "\n"
                member = MemberModel.get(member_uid)
                member_msgs, phone = _get_msgs_and_phone(member_uid)

                state, reason = _state_machine(member_msgs, phone)

                if state:
                    print state

                _state_machine_action(member, state, reason)

            except Exception as e:
                print e.message
                _print(u"Problem with member {uid} {username}".format(uid=member_uid, username=username))


    print "Browsed total {unread}".format(unread=unread_count)


if __name__ == "__main__":
    main()
