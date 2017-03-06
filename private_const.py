EMAIL = ''
PASS = ''
USERNAME = ''
MY_PHONE = ''

BASE_URL = ''
LOGIN_URL = BASE_URL + 'login'
MEMBER_URL = BASE_URL + 'member/{uid}'
MEMBER_MSG_URL = BASE_URL + 'messages/send/{uid}'
UNREAD_URL = BASE_URL + 'messages?mailbox=inbox&unread=1'
MEMBER_CONVO_URL = BASE_URL + 'messages/{convo_id}/messages'
MEMBER_PIC_URL_RE = ''
MEMBER_MSG_URL_RE = BASE_URL + 'messages/*'
MSG_URL = BASE_URL + 'messages/post'
SEARCH_URL = BASE_URL + ''

STATE_OPEN = 'OPEN'
STATE_CLOSE = 'CLOSE'
STATE_ENGAGE = 'ENGAGE'
STATE_ENGAGE_AFTER_CLOSE = 'ENGAGE_AFTER_CLOSE'

OPEN = ["",
        "",
        ""]

CLOSE = ["",
         ""]

ENGAGE = ["",
          "",
          "",
          ""]

ENGAGE_AFTER_CLOSE = ["",
                      "",
                      "",
                      ""]
