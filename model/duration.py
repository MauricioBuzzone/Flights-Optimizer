class Duration:
    def __init__(self, hours: int, minutes: int):
        self.hours = hours
        self.minutes = minutes
    def __repr__(self):
        return f'Duration(days: {self.days}, hours:{self.hours}, minutes:{self.minutes})'
    def __str__(self):
        ret = 'P'
        if self.hours > 24:
            ret += str(self.hours%24) + 'D'
            if self.hours - (self.hours%24)*24 > 0:
                ret += 'T'
                h = self.hours - (self.hours%24)*24
                ret += str(h) + 'H'
        else:
            ret += 'T'
            ret += str(self.hours) + 'H'
        if self.minutes > 0:
            ret += 'T'
            ret += str(self.minutes) + 'M'
        return ret