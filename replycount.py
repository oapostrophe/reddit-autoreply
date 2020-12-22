import time

class ReplyCount:

    def __init__(self, count, timestamp):
        self.count = count
        self.age = timestamp
    
    def increment(self, timestamp):
        self.count += 1
        self.age = timestamp