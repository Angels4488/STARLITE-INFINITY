import time

class Recorder:
    def __init__(self):
        self.logs = []
    def log(self, entry):
        self.logs.append(entry)
        print(f"LOG: {entry}")
