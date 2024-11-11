import datetime
import json


class DateTimeEncoder(json.JSONEncoder):
    def __init__(self, date_format='', **kwargs):
        super().__init__(**kwargs)
        self.date_format = date_format

    def default(self, value, date_format=''):
        if isinstance(value, datetime.datetime):
            return value.strftime(self.date_format) if self.date_format else str(value)
        else:
            return super().default(value)
