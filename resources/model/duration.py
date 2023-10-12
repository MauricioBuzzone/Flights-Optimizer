class Duration:
    def __init__(self, hours: int, minutes: int):
        self.hours = hours
        self.minutes = minutes

    def __repr__(self):
        return f'Duration(days: {self.days}, hours:{self.hours}, minutes:{self.minutes})'

    def __str__(self):
        days = self.hours % 24 if self.hours > 24 else 0
        hours = self.hours - days*24
        minutes = self.minutes

        ret = 'P'
        if days:
            ret += f'{days}D'
        if hours or minutes:
            ret += 'T'
            if hours:
                ret += f'{hours}H'
            if minutes:
                ret += f'{minutes}M'
        return ret