from __future__ import  print_function

from collections import OrderedDict
from email_repr import Email
from pytz import timezone
from termcolor import colored
import datetime
import json
import sys

ERROR_COLOR = 'red'
TIME_FORMAT = "%d/%m/%Y %H:%M:%S %z"
TIMEZONE = 'US/Pacific'
US_timezone = timezone(TIMEZONE)
NUMBER_OF_EMAILS = 'number of emails '
LAST_EMAIL = 'last email '
FIRST_EMAIL = 'first email '


class Transceiver:
    def __init__(self, name, type_name):
        self.mail_count = 0
        self.name = name
        self.type_name = type_name
        self.first_time = None
        self.last_time = None

    def insert_new_email(self, email):
        name = email.get_name(self.type_name)
        if name != self.name:
            print(colored('ERROR: Attempt to insert email on wrong', self.type_name, ERROR_COLOR))
            exit(1)

        timestamp = email.get_timestamp()
        if timestamp:

            if self.first_time:
                self.first_time = min(self.first_time, timestamp)
            else:
                self.first_time = timestamp

            if self.last_time:
                self.last_time = max(self.last_time, timestamp)
            else:
                self.last_time = timestamp

        self.mail_count += 1

    def __repr__(self):
        fields = OrderedDict()
        if self.name == Email.TYPE_SENDER:
            verb = 'sent'
        else:
            verb = 'received'
        fields[self.type_name] = self.name
        fields[NUMBER_OF_EMAILS+verb] = self.mail_count
        fields[LAST_EMAIL + verb + ' on'] = self.last_time.strftime(TIME_FORMAT)
        fields[FIRST_EMAIL + verb + ' on'] = self.first_time.strftime(TIME_FORMAT)
        return json.dumps(fields, indent=2)


class TransceiversInfo:

    FUTURE = datetime.datetime.now() + datetime.timedelta(days=100)

    def __init__(self, type_name):
        self.per_transceiver_info = {}
        self.type_name = type_name

    def insert_email(self, email):
        name = email.get_name(self.type_name)
        if name not in self.per_transceiver_info:
            self.per_transceiver_info[name] = Transceiver(name, self.type_name)
        transceiver = self.per_transceiver_info[name]
        transceiver.insert_new_email(email)

    def get_count(self):
        return len(self.per_transceiver_info)

    def __repr__(self):

        def is_naive(d):
            return d.tzinfo is None or d.tzinfo.utcoffset(d) is None

        try:
            list_of_transceivers_info = sorted(self.per_transceiver_info.values(),
                                               key=lambda x: (x.mail_count, x.last_time,
                                                              TransceiversInfo.FUTURE - x.first_time), reverse=True)
        except:
            print ([obj.last_time for obj in self.per_transceiver_info.values() if not is_naive(obj.last_time)])
            exit(2)
        return "Found "+str(self.get_count())+" "+self.type_name+"s:\n"+\
               ',\n'.join([x.__repr__() for x in list_of_transceivers_info])
