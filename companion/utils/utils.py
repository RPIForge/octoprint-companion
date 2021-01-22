#
# Generic Utils. This file hold small helper functions that don't fall under any other files
#
import pytz
from datetime import datetime

def get_now_time():
    return datetime.now(pytz.utc)

def get_now_str():
    return get_now_time().strftime("%Y-%m-%d %H:%M:%S %Z")
