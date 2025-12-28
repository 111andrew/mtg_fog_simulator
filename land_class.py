from card_class import *
import random


class Island(Card):
    def __init__(self):
        super().__init__('Island', 'land', ['basic land'], 0, 0, 0, 0, 0, 0, 0)
        self.tapped = False

    def tap_for_mana(self, mtg_play):
        assert self.tapped == False
        self.tapped = True
        mtg_play.modify_manapool(0, 1, 0, 0, 0, 0)

    def undo_tap(self, mtg_play):
        assert self.tapped == True
        self.tapped = False
        mtg_play.modify_manapool(0, -1, 0, 0, 0, 0)       

    def play(self, mtg_play):
        mtg_play.play_land(self.get_name())

    def is_tapped(self):
        return self.tapped
    
class Plains(Card):
    def __init__(self):
        super().__init__('Plains', 'land', ['basic land'], 0, 0, 0, 0, 0, 0, 0)
        self.tapped = False

    def tap_for_mana(self, mtg_play):
        assert self.tapped == False
        self.tapped = True
        mtg_play.modify_manapool(1, 0, 0, 0, 0, 0)

    def undo_tap(self, mtg_play):
        assert self.tapped == True
        self.tapped = False
        mtg_play.modify_manapool(-1, 0, 0, 0, 0, 0) 

    def play(self, mtg_play):
        mtg_play.play_land(self.get_name())

    def is_tapped(self):
        return self.tapped
    
class Fetchland(Card):
    def __init__(self):
        super().__init__('Fetchland', 'land', ['fetch land'], 0, 0, 0, 0, 0, 0, 0)
        self.tapped = False

    def tap_for_mana(self, mtg_play):
        assert self.tapped == False
        self.tapped = True
        mtg_play.modify_manapool(0, 0, 0, 0, 0, 1)

    def undo_tap(self, mtg_play):
        assert self.tapped == True
        self.tapped = False
        mtg_play.modify_manapool(0, 0, 0, 0, 0, -1)

    def play(self, mtg_play):
        mtg_play.play_land(self.get_name())

    def is_tapped(self):
        return self.tapped
    
    def crack_fetch_land(self, mtg_play, basic_land):
        # check if not tapped first
        assert self.tapped == False

        fetchland_obj = mtg_play.pop_item_by_card_name(mtg_play.battlefield, 'Fetchland')
        mtg_play.graveyard.append(fetchland_obj)

        basicland_obj = mtg_play.pop_item_by_card_name(mtg_play.deck, basic_land)
        mtg_play.battlefield.append(basicland_obj)
        random.shuffle(mtg_play.deck)
