__author__ = 'Ben'


class SubReddit:
    def __init__(self, name, count):
        self.name = name
        self.count = count

    def getname(self):
        return self.name

    def getcount(self):
        return self.count

    def addcount(self):
        self.count += 1
