from __future__ import print_function
import sys

class Email:

    TYPE_SENDER = 'sender'
    TYPE_RECEIVER = 'receiver'

    def __init__(self, sender_name, receiver_name, timestamp):

        self.sender_name = sender_name
        self.timestamp = timestamp
        self.receiver_name = receiver_name
        self.type_to_getter = {Email.TYPE_RECEIVER: self.get_receiver_name,
                               Email.TYPE_SENDER: self.get_sender_name}

    def get_sender_name(self):
        return self.sender_name

    def get_receiver_name(self):
        return self.receiver_name

    def get_name(self, type_name):
        return self.type_to_getter[type_name]()

    def get_timestamp(self):
        return self.timestamp
