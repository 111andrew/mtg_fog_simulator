import random

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
        
    def draw(self, num_cards):
        for i in range(num_cards):
            card = self.deck.pop(0)
            self.hand.append(card)

    def shuffle(self, deck):
        random.shuffle(deck)

    def modify_manapool(self, w, u, b, r, g, colorless):
        self.manapool['w'] += w
        self.manapool['u'] += u
        self.manapool['b'] += b
        self.manapool['r'] += r
        self.manapool['g'] += g
        self.manapool['colorless'] += colorless


    def play_land(self, land):
        # if fetch land in hand then play it first
        self.hand.remove(land)
        self.battlefield_append(land)
        # if 'fetch_land' in self.hand:
        #     self.hand.remove('fetch_land')
        #     self.battlefield.append('fetch_land')
        
        # if 'basic_land' in self.hand:
        #     self.hand.remove('basic_land')
        #     self.battlefield.append('basic_land')

    def crack_fetch_land(self):
        self.battlefield.remove('fetch_land')
        self.graveyard.append('fetch_land')
        self.deck.remove('basic_land')
        self.battlefield.append('basic_land')
        random.shuffle(self.deck)

    def play_nonland(self):
        self.hand.remove(card)
        self.graveyard.append(card)

    def get_deck(self):
        return self.deck