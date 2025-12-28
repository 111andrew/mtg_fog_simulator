import card_class as card

class Campfire(card.Card):
    def __init__(self):
        super().__init__('Campfire', 'artifact', ['win con', 'life gain'], 1, 0, 0, 0, 0, 0, 1)
        self.tapped = False

    # spend one generic mana to gain 2 life
    def tap_to_gain_life(self, mtg_play):
        assert self.tapped == False
        self.tapped = True
        mtg_play.modify_life(2)
        mtg_play.modify_manapool(0, 0, 0, 0, 0, -1)

    # spend two generic mana to shuffle grave into library
    def shuffle_grave_to_library(self, mtg_play):
        assert self.tapped == False
        mtg_play.modify_manapool(0, 0, 0, 0, 0, -2)
        mtg_play.deck = mtg_play.deck + mtg_play.graveyard
        mtg_play.graveyard = []
        mtg_play.shuffle()
        obj = mtg_play.pop_item_by_card_name(mtg_play.battlefield, self.get_name())
        # exile the card
        mtg_play.exile.append(obj)

    def play(self, mtg_play):
        mtg_play.play_permanent(self.get_name())

    def is_tapped(self):
        return self.tapped
