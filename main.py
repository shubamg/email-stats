from __future__ import print_function
import datetime

from email_repr import Email
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pytz import timezone
import sys
from transceiver import TransceiversInfo
from termcolor import colored
from tqdm import tqdm

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

BATCH_SIZE_FOR_PRINTING = 20
COUNT_KEY = 'count'
ERROR_COLOR = 'red'
OUTPUT_FILE_FOR_RECEIVER = 'receiver.txt'
OUTPUT_FILE_FOR_SENDER = 'sender.txt'
MISCALLANEOUS_FILE = 'miscallaneous_info.txt'
FIRST_TIME_KEY = 'first_time'
FROM_KEY = 'From'
HEADERS_KEY = 'headers'
ID_KEY = 'id'
INTERNAL_DATE_KEY = 'internalDate'
LAST_TIME_KEY = 'last_time'
MESSAGES_KEY = 'messages'
MY_EMAIL_ID = "Shubham Gupta <shubham180695.sg@gmail.com>"
MY_ID = 'me'
NAME_KEY = 'name'
NEXT_PAGE_TOKEN_KEY = 'nextPageToken'
PAYLOAD_KEY = 'payload'
RECEIVER_KEY = 'Delivered-To'
VALUE_KEY = 'value'
TIMEZONE = 'US/Pacific'
TIME_FORMAT = "%d/%m/%Y %H:%M:%S"
US_timezone = timezone(TIMEZONE)


def get_raw_messages_from_connection():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service.users().messages()


def increment_and_print(old_val, incr_amount):
    print(colored('Found {} more emails. Total {} emails found till now'.format(str(incr_amount),
                                                                                str(old_val + incr_amount)),
                  'green'))
    return old_val + incr_amount


def main():
    senders_info = TransceiversInfo(Email.TYPE_SENDER)
    receivers_info = TransceiversInfo(Email.TYPE_RECEIVER)
    message_object = get_raw_messages_from_connection()
    response = message_object.list(userId=MY_ID).execute()
    email_processed = 0
    messages = []

    num_emails_found = 0
    weird_email_count = 0 # Might be a hangout message

    def print_info():
        files_to_write = {OUTPUT_FILE_FOR_RECEIVER: open(OUTPUT_FILE_FOR_RECEIVER, 'w'),
                          OUTPUT_FILE_FOR_SENDER: open(OUTPUT_FILE_FOR_SENDER, 'w'),
                          MISCALLANEOUS_FILE: open(MISCALLANEOUS_FILE, 'w')}
        processed_status = "Processed {} emails till now!!!".format(email_processed)
        current_timestamp = datetime.datetime.now().strftime(TIME_FORMAT)
        map(lambda _file: print(current_timestamp, file=_file), files_to_write.values())
        map(lambda _file: print(processed_status, file=_file), files_to_write.values())
        print("\nFound {} weird emails".format(weird_email_count),
              file=files_to_write[MISCALLANEOUS_FILE])
        print(senders_info, '#'*100,
              file = files_to_write[OUTPUT_FILE_FOR_SENDER])
        print(receivers_info, '#'*100,
              file=files_to_write[OUTPUT_FILE_FOR_RECEIVER])
        map(lambda _file: _file.flush(), files_to_write.values())
        map(lambda _file: _file.close(), files_to_write.values())

    if MESSAGES_KEY in response:
        messages = response[MESSAGES_KEY]
        num_emails_found = increment_and_print(num_emails_found, len(messages))

    while NEXT_PAGE_TOKEN_KEY in response:
        next_page_token = response[NEXT_PAGE_TOKEN_KEY]
        response = message_object.list(userId=MY_ID, pageToken=next_page_token).execute()
        messages.extend(response[MESSAGES_KEY])
        num_emails_found = increment_and_print(num_emails_found, len(response[MESSAGES_KEY]))

        message_ids = [_dict[ID_KEY] for _dict in messages]
        for message_id in tqdm(message_ids):
            email = process_mail(message_object.get(userId=MY_ID, id=message_id).execute())
            if email:
                senders_info.insert_email(email)
                receivers_info.insert_email(email)
            else:
                print(colored('weird email ' + message_id, 'green'), file=sys.stderr)
                weird_email_count += 1
            email_processed += 1
            if email_processed % BATCH_SIZE_FOR_PRINTING == 0:
                print_info()

        messages = []


def process_mail(message):
    headers = message[PAYLOAD_KEY][HEADERS_KEY]
    internal_date = message[INTERNAL_DATE_KEY]
    if not headers:
        print (colored('ERROR: email has no headers', ERROR_COLOR), file=sys.stderr)
        return
    if not internal_date:
        print(colored('ERROR: email has no internal date', ERROR_COLOR), file=sys.stderr)
        return
    sender = None
    receiver = None
    timestamp = datetime.datetime.fromtimestamp(int(internal_date)/1000.0)
    for header in headers:
        if header[NAME_KEY] == FROM_KEY:
            sender = header[VALUE_KEY]
        elif header[NAME_KEY] == RECEIVER_KEY:
            receiver = header[VALUE_KEY]

    return Email(sender, receiver, timestamp)


if __name__ == '__main__':
    main()
