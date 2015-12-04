__author__ = 'Ben'
import re, time

# This class is used to test whether a bad source page was returned from Reddit and how long to wait between requests
# If too many requests too fast are being made the source page will only contain a warning telling me to wait n seconds


class LimitTest:
    def __init__(self, count):
        self.count=count

    def islimit(self, r):
        match = re.search(r'<title>Too Many Requests</title>', r.text)
        if match is not None:
            self.count += 1

    def getcount(self):
        return self.count

    def timeout(self, r):
        match = re.search(r'<p>please wait \d+', r.text)
        if match is not None:
            print("need to sleep for " + match.group()[15:])
            time.sleep(match.group()[15:])
            return int(match.group()[15:])
        else:
            print("dont need to sleep")
            return 0








