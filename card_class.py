class Card:
    def __init__(self, name, type, cmc, w, u, b, r, g, colorless):
        self.name = name
        # type as in permanent or non permanent
        self.type = type
        self.cmc = cmc
        self.w = w
        self.u = u
        self.b = b
        self.r = r
        self.g =g
        self.colorless = colorless
    
    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_cmc(self):
        return self.cmc
    



