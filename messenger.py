import sys
import random
import time

import requests

from private_const import MSG_URL, OPEN, CLOSE, ENGAGE, STATE_OPEN, STATE_CLOSE, STATE_ENGAGE, STATE_ENGAGE_AFTER_CLOSE, USERNAME, ENGAGE_AFTER_CLOSE
from const import COOKIES, HEADERS
from cookies import populate_cookies_dict
from helpers import _get_msgs_and_phone, _print, _get_time_stamp_and_string
from models import MemberModel


def main():
    msg_limit = int(sys.argv[1])

    print "Starting messenger...scanning db"
    populate_cookies_dict(COOKIES)
    num_msged = 0

    for member in MemberModel.scan():
        if num_msged == msg_limit:
            print "Finished messaging"
            return

        try:
            print "\n"
            msgs, phone = _get_msgs_and_phone(member.uid)

            state, reason = _state_machine(msgs, phone)

            if state:
                print state, num_msged
                num_msged += 1

            _state_machine_action(member, state, reason)
            _update_msgs(member, msgs, phone)

        except Exception as e:
            print e.message
            _print(u"Problem with member {uid} {username}. Deleting".format(uid=member.uid, username=member.username))
            member.delete()


def _state_machine_action(member, state, reason):
    if state == STATE_OPEN:
        _send_msg(member, random.choice(OPEN))
    elif state == STATE_CLOSE:
        _send_msg(member, random.choice(CLOSE))
    elif state == STATE_ENGAGE:
        _send_msg(member, random.choice(ENGAGE))
    elif state == STATE_ENGAGE_AFTER_CLOSE:
        _send_msg(member, random.choice(ENGAGE_AFTER_CLOSE))
    else:
        _print(u"Skipping {uid} {username} because {reason}".format(uid=member.uid, username=member.username, reason=reason))


def _state_machine(msgs, phone):
    reason = ''

    if not msgs:
        return STATE_OPEN, reason

    last_msg_time = msgs[-1]['created_at']

    waiting_time = 3*24*60*60
    msged_last = msgs[-1]['username'] == USERNAME
    time_passed = _has_time_passed(last_msg_time, waiting_time)
    can_reply = not msged_last or time_passed

    if not can_reply:
        if msged_last and not time_passed:
            reason = 'you msged last and not enough time has passed'
        elif msged_last:
            reason = 'you msged last'
        elif not time_passed:
            reason = 'not enough time has passed'
        return None, reason

    current_state = None
    engage_after_close_count = 0
    for msg in msgs:
        if msg['msg'] in OPEN:
            current_state = STATE_OPEN
        if msg['msg'] in CLOSE:
            current_state = STATE_CLOSE
        if msg['msg'] in ENGAGE:
            current_state = STATE_ENGAGE
        if msg['msg'] in ENGAGE_AFTER_CLOSE:
            current_state = ENGAGE_AFTER_CLOSE
            engage_after_close_count += 1

    if phone:
        waiting_time = 5*24*60*60
        if _has_time_passed(last_msg_time, waiting_time) and engage_after_close_count < 3:
            return STATE_ENGAGE_AFTER_CLOSE, reason
        else:
            return None, 'got number but not enough time has passed'

    if current_state == STATE_OPEN or current_state == STATE_ENGAGE:
        return STATE_CLOSE, reason
    else:
        return STATE_ENGAGE, reason


def _has_time_passed(last_msg_time, waiting_time):
    time_stamp, _ = _get_time_stamp_and_string(last_msg_time)
    return time_stamp < (time.time() - waiting_time)


def _send_msg(member, msg):
    time.sleep(random.randint(1,6))
    data = {
        'member_uid': member.uid,
        'body': msg
    }
    try:
        requests.post(MSG_URL, data=data, cookies=COOKIES, headers=HEADERS)
        _print(u"Sent {msg} to {uid} {username}".format(msg=msg, uid=member.uid, username=member.username))
    except Exception as e:
        print e.message
        _print(u"Couldn't send message to {uid} {username}".format(uid=member.uid, username=member.username))


def _update_msgs(member, msgs, phone):
    try:
        member.msgs = msgs
        member.phone = phone
        member.save()
    except:
        pass


if __name__ == "__main__":
    main()
