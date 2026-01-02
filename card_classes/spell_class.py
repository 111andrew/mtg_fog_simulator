import card_classes.card_class as card


################### fog spells
class HolyDay(card.Card):
    def __init__(self):
        super().__init__('HolyDay', 'Spell', ['fog'], 1, 1, 0, 0, 0, 0, 0)
    
    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.set_fog()


class MomentOfSilence(card.Card):
    def __init__(self):
        super().__init__('MomentOfSilence', 'Spell', ['fog'], 1, 1, 0, 0, 0, 0, 0)
    
    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.set_fog()


class EtherealHaze(card.Card):
    def __init__(self):
        super().__init__('EtherealHaze', 'Spell', ['fog'], 1, 1, 0, 0, 0, 0, 0)
    
    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.set_fog()


class FalsePeace(card.Card):
    def __init__(self):
        super().__init__('FalsePeace', 'Spell', ['fog'], 1, 1, 0, 0, 0, 0, 0)
    
    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.set_fog()


class DawnCharm(card.Card):
    def __init__(self):
        super().__init__('DawnCharm', 'Spell', ['fog'], 2, 1, 0, 0, 0, 0, 1)
    
    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.set_fog()


class AngelSong(card.Card):
    def __init__(self):
        super().__init__('AngelSong', 'Spell', ['fog'], 2, 1, 0, 0, 0, 0, 1)
    
    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.set_fog()


# riot control prevents all damage --> super fog
# gains life equal to number of opponent creatures, assume 3
class RiotControl(card.Card):
    def __init__(self):
        super().__init__('RiotControl', 'Spell', ['fog', 'life gain'], 3, 1, 0, 0, 0, 0, 2)
    
    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.set_fog()
        mtg_play.set_no_damage()
        mtg_play.modify_life(3)


################### draw spells
class WordsOfWisdom(card.Card):
    def __init__(self):
        super().__init__('WordsOfWisdom', 'Spell', ['draw'], 2, 0, 1, 0, 0, 0, 1)
        self.draw_amount = 2

    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.draw(self.draw_amount)


# a counterspell, but self replaces so counts as draw here
class ArcaneDenial(card.Card):
    def __init__(self):
        super().__init__('ArcaneDenial', 'Spell', ['draw'], 2, 0, 1, 0, 0, 0, 1)
        self.draw_amount = 1

    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.draw(self.draw_amount)


class AbandonAttachment(card.Card):
    def __init__(self):
        super().__init__('AbandonAttachment', 'Spell', ['draw', 'loot'], 2, 0, 1, 0, 0, 0, 1)
        self.draw_amount = 2

    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        # try to discard 'draws more' cards if the draw amount is only 1
        card_to_discard = False
        for card in mtg_play.hand:
            if card.has_purpose('draws more'):
                card.update_draw_amount(mtg_play)
                if card.draw_amount < 2:
                    card_to_discard = card.get_name()
        if not card_to_discard:
            card_to_discard = mtg_play.determine_card_to_discard()
        mtg_play.discard(card_to_discard)
        mtg_play.draw(self.draw_amount)

    # has to also have at least another card in hand to discard
    def can_pay_cmc(self, mtg_play):
        can_pay = True
        # check first for colored mana
        if self.w > mtg_play.get_manapool()['w']:
            can_pay = False
        if self.u > mtg_play.get_manapool()['u']:
            can_pay = False
        if self.b > mtg_play.get_manapool()['b']:
            can_pay = False
        if self.r > mtg_play.get_manapool()['r']:
            can_pay = False
        if self.g > mtg_play.get_manapool()['g']:
            can_pay = False
        # check colorless by looking at all cmc
        total_cost = self.w + self.u + self.b + self.r + self.g + self.colorless
        if total_cost > mtg_play.get_total_mana():
            can_pay = False
        if len(mtg_play.hand) < 2:
            can_pay = False
        return can_pay

    

    def loot_opportunity(self, mtg_play):
        should_loot = False
        for card in mtg_play.hand:
            if card.has_purpose('draws more'):
                card.update_draw_amount(mtg_play)
                if card.draw_amount < 2:
                    should_loot = True
        return should_loot


# draws 1 + the amount of accumulated knowledges in the grave
class AccumulatedKnowledge(card.Card):
    def __init__(self):
        super().__init__('AccumulatedKnowledge', 'Spell', ['draw', 'draws more'], 2, 0, 1, 0, 0, 0, 1)
        self.draw_amount = 1

    def update_draw_amount(self, mtg_play):
        graveyard_dict = mtg_play.get_card_counts(mtg_play.graveyard)
        if 'AccumulatedKnowledge' in graveyard_dict.keys():
            self.draw_amount = graveyard_dict['AccumulatedKnowledge'] + 1
        else:
            self.draw_amount = 1

    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        self.update_draw_amount(mtg_play)
        mtg_play.draw(self.draw_amount)


# draws 1 + the amount of take inventory in the grave
class TakeInventory(card.Card):
    def __init__(self):
        super().__init__('TakeInventory', 'Spell', ['draw', 'draws more'], 2, 0, 1, 0, 0, 0, 1)
        self.draw_amount = 1

    def update_draw_amount(self, mtg_play):
        graveyard_dict = mtg_play.get_card_counts(mtg_play.graveyard)
        if 'TakeInventory' in graveyard_dict.keys():
            self.draw_amount = graveyard_dict['TakeInventory'] + 1
        else:
            self.draw_amount = 1

    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        self.update_draw_amount(mtg_play)
        mtg_play.draw(self.draw_amount)

# draw 3, then put 2 cards back to top
class Brainstorm(card.Card):
    def __init__(self):
        super().__init__('Brainstorm', 'Spell', ['draw'], 1, 0, 1, 0, 0, 0, 0)
        self.draw_amount = 3

    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.draw(self.draw_amount)
        # put two cards back
        for i in range(2):
            card_to_discard = mtg_play.determine_card_to_discard()
            mtg_play.put_card_to_deck_top(card_to_discard)


# draws a card for each attacking, just assume, draws 3 for now
class KeepWatch(card.Card):
    def __init__(self):
        super().__init__('KeepWatch', 'Spell', ['draw'], 3, 0, 1, 0, 0, 0, 2)
        self.draw_amount = 3

    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.draw(self.draw_amount)


# draws a cards and gains life to number of cards in hand
class UnionOfTheThirdPath(card.Card):
    def __init__(self):
        super().__init__('UnionOfTheThirdPath', 'Spell', ['draw', 'life gain'], 3, 1, 0, 0, 0, 0, 2)
        self.draw_amount = 1

    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.draw(self.draw_amount)
        mtg_play.modify_life(len(mtg_play.hand))


class LorienRevealed(card.Card):
    def __init__(self):
        super().__init__('LorienRevealed', 'Spell', ['draw', 'land cycle'], 5, 0, 2, 0, 0, 0, 3)
        self.draw_amount = 3
        self.ability_cost = 1

    def play(self, mtg_play):
        mtg_play.play_spell(self.get_name())
        mtg_play.draw(self.draw_amount)

    def land_cycle(self, mtg_play):
        mtg_play.land_cycle(self.get_name(), 'Island', self.ability_cost)

    def can_cycle(self, mtg_play):
        can_cycle = True
        # check that island is in deck and has mana to pay
        deck_list = mtg_play.get_card_counts(mtg_play.deck)
        if 'Island' not in deck_list.keys():
            can_cycle = False
        
        if not self.can_pay_mana(0,0,0,0,0,1,mtg_play):
            can_cycle = False
        return can_cycle
    
