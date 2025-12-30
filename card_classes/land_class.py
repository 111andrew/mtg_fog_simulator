from card_classes.card_class import *
import random

class LandClass(Card):

    def tap_for_mana(self, mtg_play):
        assert self.tapped == False
        self.tapped = True
        mtg_play.modify_manapool(self.generate_mana['w'], 
                                 self.generate_mana['u'], 
                                 self.generate_mana['b'], 
                                 self.generate_mana['r'], 
                                 self.generate_mana['g'], 
                                 self.generate_mana['colorless'])

    def undo_tap(self, mtg_play):
        assert self.tapped == True
        self.tapped = False
        mtg_play.modify_manapool(-self.generate_mana['w'], 
                                 -self.generate_mana['u'], 
                                 -self.generate_mana['b'], 
                                 -self.generate_mana['r'], 
                                 -self.generate_mana['g'], 
                                 -self.generate_mana['colorless'])    

    def play(self, mtg_play):
        mtg_play.play_land(self.get_name())

    def is_tapped(self):
        return self.tapped


class Island(LandClass):
    def __init__(self):
        super().__init__('Island', 'land', ['basic land'], 0, 0, 0, 0, 0, 0, 0)
        self.tapped = False
        self.generate_mana = {
            'w':0,
            'u':1,
            'b':0,
            'r':0,
            'g':0,
            'colorless':0
        }

    
class Plains(LandClass):
    def __init__(self):
        super().__init__('Plains', 'land', ['basic land'], 0, 0, 0, 0, 0, 0, 0)
        self.tapped = False
        self.generate_mana = {
            'w':1,
            'u':0,
            'b':0,
            'r':0,
            'g':0,
            'colorless':0
        }


    
class Fetchland(LandClass):
    def __init__(self):
        super().__init__('Fetchland', 'land', ['fetch land'], 0, 0, 0, 0, 0, 0, 0)
        self.tapped = False
        self.generate_mana = {
            'w':0,
            'u':0,
            'b':0,
            'r':0,
            'g':0,
            'colorless':1
        }
    
    def crack_fetch_land(self, mtg_play, basic_land):
        # check if not tapped first
        assert self.tapped == False

        fetchland_obj = mtg_play.pop_item_by_card_name(mtg_play.battlefield, 'Fetchland')
        mtg_play.graveyard.append(fetchland_obj)

        basicland_obj = mtg_play.pop_item_by_card_name(mtg_play.deck, basic_land)
        mtg_play.battlefield.append(basicland_obj)
        random.shuffle(mtg_play.deck)
