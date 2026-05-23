class Counter:
    def __init__(self, start=0):
        self.count = start

    def next(self):
        self.count += 1
        return self.count