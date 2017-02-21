from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, UnicodeSetAttribute, JSONAttribute
import time


class MemberModel(Model):
    class Meta:
        table_name = 'members'
        region = 'us-west-2'
        read_capacity_units = 5
        write_capacity_units = 5

    uid = UnicodeAttribute(hash_key=True)
    last_logged_in_stamp = NumberAttribute(default=time.time())
    last_logged_in = UnicodeAttribute(default='')
    username = UnicodeAttribute(default='')
    location = UnicodeAttribute(default='')
    pics = UnicodeSetAttribute(default=set())
    msgs = JSONAttribute(default=[])
    phone = UnicodeAttribute(default='')
    last_updated = NumberAttribute(default=time.time())
    last_full_updated = NumberAttribute(default=0)
