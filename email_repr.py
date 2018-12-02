class Email:
    def __init__(self, sender_name, timestamp):
        self.sender_name = sender_name
        self.timestamp = timestamp

    def get_sender_name(self):
        return self.sender_name

    def get_timestamp(self):
        return self.timestamp
