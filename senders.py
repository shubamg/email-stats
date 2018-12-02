from collections import OrderedDict
from pytz import timezone
from termcolor import colored
import json


ERROR_COLOR = 'red'
TIME_FORMAT = "%d/%m/%Y %H:%M:%S"
TIMEZONE = 'US/Pacific'
US_timezone = timezone(TIMEZONE)


class Sender:
    def __init__(self, sender_name):
        self.mail_count = 0
        self.sender_name = sender_name
        self.first_time = None
        self.last_time = None

    def insert_new_email(self, email):
        sender_name = email.get_sender_name()
        if sender_name != self.sender_name:
            print(colored('ERROR: Attempt to insert email on wrong sender', ERROR_COLOR))
            exit(1)
        timestamp = email.get_timestamp()
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
        fields['sender'] = self.sender_name
        fields['number of emails received'] = self.mail_count
        print self.last_time
        print self.first_time
        fields['last email sent on'] = self.last_time.astimezone(US_timezone).strftime(TIME_FORMAT)
        fields['first email sent on'] = self.first_time.astimezone(US_timezone).strftime(TIME_FORMAT)
        return json.dumps(fields, indent=2)


class SendersInfo:
    def __init__(self):
        self.per_sender_info = {}

    def insert_email(self, email):
        sender_name = email.get_sender_name()
        if sender_name not in self.per_sender_info:
            self.per_sender_info[sender_name] = Sender(sender_name)
        sender = self.per_sender_info[sender_name]
        sender.insert_new_email(email)

    def __repr__(self):
        list_of_senders_info = sorted(self.per_sender_info.values(), key=lambda x: (x.mail_count, x.last_time),
                                      reverse=True)
        return ''.join([x.__repr__() for x in list_of_senders_info])
