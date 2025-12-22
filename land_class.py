from card_class import *
import random

class Island(Card):
    def __init__(self):
        super().__init__('Island', 'permanent', 0, 0, 0, 0, 0, 0, 0)
        self.status = 'untapped'

    def tap_for_mana(self, mtg_play):
        self.status = 'tapped'
        mtg_play.modify_manapool(0, 1, 0, 0, 0, 0)

    def play(self, mtg_play):
        mtg_play.play_land(self)

    def get_status(self):
        return self.status
    
class Plains(Card):
    def __init__(self):
        super().__init__('Plains', 'permanent', 0, 0, 0, 0, 0, 0, 0)
        self.status = 'untapped'

    def tap_for_mana(self, mtg_play):
        self.status = 'tapped'
        mtg_play.modify_manapool(1, 0, 0, 0, 0, 0)

    def play(self, mtg_play):
        mtg_play.play_land(self)

    def get_status(self):
        return self.status
    
class Fetchland(Card):
    def __init__(self):
        super().__init__('Fetchland', 'permanent', 0, 0, 0, 0, 0, 0, 0)
        self.status = 'untapped'

    def tap_for_mana(self, mtg_play):
        self.status = 'tapped'
        mtg_play.modify_manapool(0, 0, 0, 0, 0, 1)

    def play(self, mtg_play):
        mtg_play.play_land(self)

    def get_status(self):
        return self.status
    
    def crack_fetch_land(self, mtg_play, basic_land):
        mtg_play.battlefield.remove('Fetchland')
        mtg_play.graveyard.append('Fetchland')
        mtg_play.deck.remove(basic_land)
        mtg_play.battlefield.append(basic_land)
        random.shuffle(mtg_play.deck)