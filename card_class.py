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

class Island(Card):
    def __init__(self):
        super().__init__('basic_land', 'permanent', 0, 0, 0, 0, 0, 0, 0)
        self.status = 'untapped'

    def tap_for_mana(self, mtg_play):
        self.status = 'tapped'
        mtg_play.modify_manapool(0, 1, 0, 0, 0, 0)

    def play(self, mtg_play):
        mtg_play.play_land(self)

    def get_status(self):
        return self.status

