import decimal
from datetime import date
import json
from datetime import datetime

class JsonCustomEncoder(json.JSONEncoder):

    def default(self, value):
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        elif isinstance(value, decimal.Decimal):
            return "%2.2f"%value
        else:
            return json.JSONEncoder.default(self, value)


def rpc_dumps(value):
    return json.dumps(value, cls=JsonCustomEncoder)