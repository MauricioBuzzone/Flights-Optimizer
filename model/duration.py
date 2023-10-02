class Duration:
    def __init__(self, days: int, hours: int, minutes: int):
        self.days = days
        self.hours = hours
        self.minutes = minutes
    def __repr__(self):
        return f'Duration(days: {self.days}, hours:{self.hours}, minutes:{self.minutes})'
    def __str__(self):
        return f'Duration(days: {self.days}, hours:{self.hours}, minutes:{self.minutes})'