import random
from land_class import *


class mtg_play():
    def __init__(self, deck_dict):
        self.deck = []
        self.hand = []
        self.exile = []
        self.life = 20
        self.manapool = {
            'w':0,
            'u':0,
            'b':0,
            'r':0,
            'g':0,
            'colorless':0
        }
        self.graveyard = []
        # for card in deck_dict.keys():
        #     self.deck.extend(deck_dict[card] * [card])

        get_class = lambda x: globals()[x]
        for card in deck_dict.keys():
            for i in range(deck_dict[card]):
                self.deck.append(get_class(card)())

    def modify_life(self, lifegain):
        self.life += lifegain
        
    def draw(self, num_cards):
        for i in range(num_cards):
            card = self.deck.pop(0)
            self.hand.append(card)

    def shuffle(self):
        random.shuffle(self.deck)

    def modify_manapool(self, w, u, b, r, g, colorless):
    
        self.manapool['w'] += w
        self.manapool['u'] += u
        self.manapool['b'] += b
        self.manapool['r'] += r
        self.manapool['g'] += g
        self.manapool['colorless'] += colorless

        total_mana = 0
        for color in self.manapool:
            total_mana += self.manapool[color]

        # make sure total mana >= 0
        assert total_mana >= 0

    def play_land(self, land):
        # if fetch land in hand then play it first
        land_obj = self.pop_item_by_card_name(self.hand, land)
        self.battlefield.append(land_obj)

    def play_spell(self, card):
        spell_obj = self.pop_item_by_card_name(self.hand, card)
        self.graveyard.append(spell_obj)

    def play_permanent(self, card):
        permanent_obj = self.pop_item_by_card_name(self.hand, card)
        self.battlefield.append(permanent_obj)

    def get_deck(self):
        return self.deck
    
    # gotta write a function instead of using remove
    def pop_item_by_card_name(self, list, card_name):
        for idx, card in enumerate(list):
            if card.get_name() == card_name:
                first_index = idx
                break
        return list.pop(first_index)

