from datetime import datetime, timedelta
import dateutil.parser

class TimeFormat(object):

    def __init__(self, utc_str):
        self.utc = dateutil.parser.parse(utc_str).replace(tzinfo=None)
        self.local_time = self.utc.replace(tzinfo=dateutil.tz.tzutc()
                                   ).astimezone(dateutil.tz.tzlocal())

    def get_local_time(self):
        datetime_format = '%y-%m-%d' \
            if datetime.utcnow() - self.utc >= timedelta(days=1) \
            else '%H:%M:%S'

        return self.local_time.strftime(datetime_format)
