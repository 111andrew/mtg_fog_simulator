import card_class as card

class JacesErasure(card.Card):
    def __init__(self):
        super().__init__('JacesErasure', 'enchantment', ['win con'], 2, 0, 1, 0, 0, 0, 1)
        self.tapped = False

    def play(self, mtg_play):
        mtg_play.play_permanent(self.get_name())
        # set ability into status
        mtg_play.status.append('JacesErasure')
