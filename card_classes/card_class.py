class Card:
    def __init__(self, name, type, purpose, cmc, w, u, b, r, g, colorless):
        self.name = name
        # type as in permanent or non permanent
        self.type = type
        self.purpose = purpose
        self.cmc = cmc
        self.w = w
        self.u = u
        self.b = b
        self.r = r
        self.g = g
        self.colorless = colorless
    
    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_cmc(self):
        return self.cmc
    
    def get_purpose(self):
        return self.purpose
    
    def has_purpose(self, target_purpose):
        return target_purpose in self.purpose
    
    def can_pay_mana(self, w, u, b, r, g, colorless, mtg_play):
        can_pay = True
        # check first for colored mana
        if w > mtg_play.get_manapool()['w']:
            can_pay = False
        if u > mtg_play.get_manapool()['u']:
            can_pay = False
        if b > mtg_play.get_manapool()['b']:
            can_pay = False
        if r > mtg_play.get_manapool()['r']:
            can_pay = False
        if g > mtg_play.get_manapool()['g']:
            can_pay = False
        # check colorless by looking at all cmc
        total_cost = w + u + b + r + g + colorless
        if total_cost > mtg_play.get_total_mana():
            can_pay = False
        return can_pay

    def can_pay_cmc(self, mtg_play):
        can_pay = True
        # check first for colored mana
        if self.w > mtg_play.get_manapool()['w']:
            can_pay = False
        if self.u > mtg_play.get_manapool()['u']:
            can_pay = False
        if self.b > mtg_play.get_manapool()['b']:
            can_pay = False
        if self.r > mtg_play.get_manapool()['r']:
            can_pay = False
        if self.g > mtg_play.get_manapool()['g']:
            can_pay = False
        # check colorless by looking at all cmc
        total_cost = self.w + self.u + self.b + self.r + self.g + self.colorless
        if total_cost > mtg_play.get_total_mana():
            can_pay = False
        return can_pay
