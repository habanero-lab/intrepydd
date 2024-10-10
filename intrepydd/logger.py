class Logger(object):
    def __init__(self, fn):
        self.file = open(fn, 'w')

    def open_tag(self, name):
        print("<%s>" % name, file=self.file)

    def close_tag(self, name):
        print("</%s>" % name, file=self.file)

    def print(self, *args):
        for s in args:
            print(str(s).replace('<', '['), file=self.file)
        
