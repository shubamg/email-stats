from __future__ import print_function
from dateutil.parser import parse
from email_repr import Email
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from senders import SendersInfo
from termcolor import colored
from tqdm import tqdm

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

MY_ID = 'me'
NAME_KEY = 'name'
PAYLOAD_KEY = 'payload'
HEADERS_KEY = 'headers'
VALUE_KEY = 'value'
ID_KEY = 'id'
ERROR_COLOR = 'red'
MESSAGES_KEY = 'messages'
FROM_KEY = 'From'
DATE_KEY = 'Date'
COUNT_KEY = 'count'
FIRST_TIME_KEY = 'first_time'
LAST_TIME_KEY = 'last_time'
MY_EMAIL_ID = "Shubham Gupta <shubham180695.sg@gmail.com>"


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


def main():
    senders_info = SendersInfo()
    message_object = get_raw_messages_from_connection()
    page_of_messages = message_object.list(userId=MY_ID).execute()
    messages = page_of_messages[MESSAGES_KEY]
    email_processed = 0
    sent_emails = 0
    message_ids = [_dict[ID_KEY] for _dict in messages]
    for message_num in tqdm(xrange(len(message_ids))):
        email = process_mail(message_object.get(userId=MY_ID, id=message_ids[message_num]).execute())
        if email:
            senders_info.insert_email(email)
        else:
            sent_emails += 1
        email_processed += 1
    print(senders_info)


def process_mail(message):
    headers = message[PAYLOAD_KEY][HEADERS_KEY]
    if not headers:
        print (colored(ERROR_COLOR,'ERROR: email has no headers'))
        exit(1)
    sender = None
    timestamp = None
    for header in headers:
        if header[NAME_KEY] == FROM_KEY:
            sender = header[VALUE_KEY]
        elif header[NAME_KEY] == DATE_KEY:
            timestamp = parse(header[VALUE_KEY])
    if not (sender or timestamp):
        print(colored(ERROR_COLOR, 'ERROR: Either sender info or timestamp or both are missing'))
        exit(1)
    if sender == MY_EMAIL_ID:
        return None
    return Email(sender, timestamp)


if __name__ == '__main__':
    main()
