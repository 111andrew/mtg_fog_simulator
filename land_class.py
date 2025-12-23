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
        mtg_play.play_land(self.get_name())

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
        mtg_play.play_land(self.get_name())

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
        mtg_play.play_land(self.get_name())

    def get_status(self):
        return self.status
    
    def crack_fetch_land(self, mtg_play, basic_land):
        fetchland_obj = mtg_play.pop_item_by_card_name(mtg_play.battlefield, 'Fetchland')
        mtg_play.graveyard.append(fetchland_obj)

        basicland_obj = mtg_play.pop_item_by_card_name(mtg_play.deck, basic_land)
        mtg_play.battlefield.append(basicland_obj)
        random.shuffle(mtg_play.deck)