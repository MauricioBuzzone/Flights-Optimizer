class Airport:
    def __init__(self, cod:str, latitude:float, longitude:float):
        self.cod = cod
        self.latitude = latitude
        self.longitude = longitude
    def __repr__(self):
        return f'Airport(cod: {self.cod}, latitude:{self.latitude}, longitude:{self.longitude})'
    def __str__(self):
        return f'Airport(cod: {self.cod}, latitude:{self.latitude}, longitude:{self.longitude})'