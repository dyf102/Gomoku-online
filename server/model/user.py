
IDLE = 0
OFFLINE = 1
INGAME = 2

class User(object):

    def __init__(self, username, uid, point=0, status=IDLE):
        self.username = username
        self.uid = uid
        self.point = point
        self.status = status

    def ___str__(self):
        return '{} {} {} {}'.format(self.username, self.uid, self.point, self.is_idle)

    def __eq__(self, other):
        return self.username == other.username and self.uid == other.uid

