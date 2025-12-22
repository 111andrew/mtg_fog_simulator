import random
from land_class import *


class mtg_play():
    def __init__(self, deck_dict):
        self.deck = []
        self.hand = []
        self.manapool = {
            'w':0,
            'u':0,
            'b':0,
            'r':0,
            'g':0,
            'colorless':0
        }
        self.graveyard = []
        for card in deck_dict.keys():
            self.deck.extend(deck_dict[card] * [card])

        get_class = lambda x: globals()[x]
        for card in deck_dict.keys():
            for i in range(deck_dict[card]):
                self.deck.append(get_class(card)())
        
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

    def play_land(self, land):
        # if fetch land in hand then play it first
        self.pop_item_by_card_name(self.hand, land)
        self.battlefield_append(land)

    def play_nonland(self, card):
        self.pop_item_by_card_name(self.hand, card)
        self.graveyard.append(card)

    def get_deck(self):
        return self.deck
    
    # gotta write a function instead of using remove
    def pop_item_by_card_name(self, list, card_name):
        for idx, card in enumerate(list):
            if card.get_name() == card_name:
                first_index = idx
                break
        return list.pop(first_index)

