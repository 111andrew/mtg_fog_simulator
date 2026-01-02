import random
from card_classes.land_class import *
from card_classes.artifact_class import *
from card_classes.spell_class import *
from card_classes.enchantment_class import *
from card_classes.creature_class import *
import sys
import logging

logger = logging.getLogger("mtg_play_class")
logging.basicConfig(format='%(message)s', stream=sys.stdout, level=logging.CRITICAL)

class mtg_play():
    def __init__(self, deck_dict):
        self.deck = []
        self.hand = []
        self.exile = []
        self.battlefield = []
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
        self.deck_dict = deck_dict
        self.mulligan_count = 0

        self.land_played_this_turn = False

        # start out with opponent starting hand considered
        self.opponent_milled = 7
        self.opponent_milled_to_win = 60
        self.lost = False
        self.win = False

        # results counter
        self.fog_missed = 0
        self.fog_turns = 0

        self.status = []

        get_class = lambda x: globals()[x]
        for card in deck_dict.keys():
            for i in range(deck_dict[card]):
                self.deck.append(get_class(card)())

    def modify_life(self, lifegain):
        self.life += lifegain
        logger.info("life total change: " + str(lifegain))
        if self.life < 1:
            self.lost = True
        
    def draw(self, num_cards):
        for i in range(num_cards):
            # check if self milled out
            if len(self.deck) == 0:
                self.lost = True
            else:
                card = self.deck.pop(0)
                self.hand.append(card)
            jaces_erasure_count = self.status.count("JacesErasure")
            self.modify_opponent_milled(jaces_erasure_count)
    
    def discard(self, card_name):
        # if fetch land in hand then play it first
        card_obj = self.pop_item_by_card_name(self.hand, card_name)
        self.graveyard.append(card_obj)
        logger.info("discard card: " + card_obj.get_name())

    def put_card_to_deck_top(self, card_name):
        logger.info("Put card on deck top: " + card_name)
        card_obj = self.pop_item_by_card_name(self.hand, card_name)
        self.deck.insert(0, card_obj)

    def put_card_to_deck_bottom(self, card_name):
        logger.info("Put card on deck bottom: " + card_name)
        card_obj = self.pop_item_by_card_name(self.hand, card_name)
        self.deck.append(card_obj)
        
    def shuffle(self):
        random.shuffle(self.deck)

    def modify_opponent_milled(self, milled):
        self.opponent_milled += milled
        logger.info(self.get_card_counts(self.battlefield))
        logger.info("opponent milled: " + str(milled) + " total milled: " + str(self.opponent_milled) )
        if self.opponent_milled > self.opponent_milled_to_win:
            self.win = True

    ########################### mulligan
    def determine_and_mulligan(self):
        should_mulligan = True

        while should_mulligan:
        
            # mulligan if 0 lands or > 4 lands
            hand_dict = self.get_card_type_counts(self.hand)

            # pseudo_land_count = 0
            # # count also land cyclers
            # for card in self.hand:
            #     if card.get_type() == 'land' or card.has_purpose('land cycle'):
            #         pseudo_land_count += 1

            if 'land' in hand_dict.keys():
                if hand_dict['land'] > 4 or hand_dict['land'] < 2:
                    should_mulligan = True
                else:
                    should_mulligan = False
            # else means there's no lands
            else:
                should_mulligan = True

            # only mulligan at most 2 times
            if self.mulligan_count > 1:
                should_mulligan = False
            
            if should_mulligan:
                self.mulligan_count += 1

                logger.info("mulliganing!")
                logger.info(self.pretty_list(self.hand))
                
                # refresh deck and hand
                self.deck = self.deck + self.hand
                self.hand = []
                self.shuffle()
                self.draw(7)

                for i in range(self.mulligan_count):
                    card_to_discard = self.determine_card_to_discard()
                    self.put_card_to_deck_bottom(card_to_discard)

                logger.info("new hand: ")
                logger.info(self.pretty_list(self.hand))
        
    ########################### mana related

    def float_all_mana(self):
        for card in self.battlefield:
            if card.get_type() == 'land':
                if card.tapped == False:
                    card.tap_for_mana(self)

    def unfloat_all_mana(self):
        for card in self.battlefield:
            if card.get_type() == 'land':
                card.undo_tap(self)

    def empty_manapool(self):
        self.manapool['w'] = 0
        self.manapool['u'] = 0
        self.manapool['b'] = 0
        self.manapool['r'] = 0
        self.manapool['g'] = 0
        self.manapool['colorless'] = 0

    def modify_manapool(self, w, u, b, r, g, colorless):
        self.manapool['w'] += w
        self.manapool['u'] += u
        self.manapool['b'] += b
        self.manapool['r'] += r
        self.manapool['g'] += g
        self.manapool['colorless'] += colorless

        # make sure total mana >= 0
        assert self.get_total_mana() >= 0
        assert self.manapool['w'] >= 0
        assert self.manapool['u'] >= 0

    def get_manapool(self):
        return self.manapool

    def get_total_mana(self):
        total_mana = 0
        for color in self.manapool:
            total_mana += self.manapool[color]
        return total_mana
    
    #################### upkeep
    def upkeep(self):
        self.land_played_this_turn = False

        # reset the fog status
        self.unset_fog()
        self.unset_no_damage()

    #################### end step items
    def untap_all(self):
        for card in self.battlefield:
            card.tapped=False
    
    def end_step(self):
        # empty all mana
        self.empty_manapool()
        # discard to 7 cards
        while len(self.hand) > 7:
            card_to_discard = self.determine_card_to_discard()
            # logger.info("discard to handsize: " + card_to_discard)
            self.discard(card_to_discard)

        # opponent draws one at their turn
        self.modify_opponent_milled(1)

    ##################### playing items

    def can_pay_card_name(self, list, card_name):
        idx = self.find_card_index(list, card_name)
        return list[idx].can_pay_cmc(self)

    def play_land(self, land):
        # if fetch land in hand then play it first
        land_obj = self.pop_item_by_card_name(self.hand, land)
        self.battlefield.append(land_obj)

    def play_spell(self, card_name):
        spell_obj = self.pop_item_by_card_name(self.hand, card_name)
        # pay for spell
        self.modify_manapool(
                w = 0-spell_obj.w,
                u = 0-spell_obj.u,
                b = 0-spell_obj.b,
                r = 0-spell_obj.r,
                g = 0-spell_obj.g,
                colorless = 0-spell_obj.colorless
        )
        logger.info('played spell: new manapool')
        logger.info(self.manapool)
        self.graveyard.append(spell_obj)

    def play_permanent(self, card_name):
        permanent_obj = self.pop_item_by_card_name(self.hand, card_name)
        # pay for spell
        self.modify_manapool(
                w = 0-permanent_obj.w,
                u = 0-permanent_obj.u,
                b = 0-permanent_obj.b,
                r = 0-permanent_obj.r,
                g = 0-permanent_obj.g,
                colorless=0-permanent_obj.colorless
        )

        assert self.get_total_mana() >= 0
        self.battlefield.append(permanent_obj)

    def land_cycle(self, card_name, target_land, mana_cost):
        # pay for ability
        self.modify_manapool(
                w = 0,
                u = 0,
                b = 0,
                r = 0,
                g = 0,
                colorless=-mana_cost
        )

        assert self.get_total_mana() >= 0
        card_obj = self.pop_item_by_card_name(self.hand, card_name)
        self.graveyard.append(card_obj)
        target_land_obj = self.pop_item_by_card_name(self.deck, target_land)
        self.hand.append(target_land_obj)
        self.shuffle()

    ################### game determinations

    def determine_and_play_fog(self):
        # sort hand by highest cmc
        self.sort_list_by_cmc(self.hand)
        # go through cards by cmc order and see if its a fog
        # try to cast the highest cmc fog able
        for card in self.hand:
            if card.has_purpose('fog') and 'fog' not in self.status:
                # try to see if can cast it
                if card.can_pay_cmc(self):
                    logger.info("cast fog: " + card.get_name())
                    card.play(self)

    def determine_and_play_wincons(self):
        for card in self.hand:
            if card.has_purpose('win con'):
                if card.can_pay_cmc(self):
                    logger.info("cast wincon: " + card.get_name())
                    card.play(self)

    def determine_and_play_lifegain(self):
        if self.life < 9:
            for card in self.hand:
                if card.has_purpose('life gain'):
                    if card.can_pay_cmc(self):
                        logger.info("cast life gain: " + card.get_name())
                        card.play(self)

    def determine_and_play_monarch(self):
        if 'monarch' not in self.status:
            for card in self.hand:
                if card.has_purpose('monarch'):
                    if card.can_pay_cmc(self):
                        logger.info("cast monarch: " + card.get_name())
                        card.play(self)

    def determine_cast_more_draw_spells(self):
        # simple rules for now, can be more complicated in future
        while len(self.hand) < 8 and self.can_cast_draw():
            self.determine_and_play_one_draw()

    def determine_and_play_loot(self):
        for card in self.hand:
            if card.has_purpose('loot'):
                should_loot = card.loot_opportunity(self)
                if should_loot:
                    if card.can_pay_cmc(self):
                        card.play(self)

    def determine_and_play_one_draw(self):
        # if fogged already --> cast most expensive draw
        if 'fog' in self.status:
            # sort hand by highest cmc first
            self.sort_list_by_cmc(self.hand)
            for idx, card in enumerate(self.hand):
                if card.has_purpose('draw'):
                    if card.has_purpose('draws more'):
                        card.update_draw_amount(self)
                    # try to leave at least one card in deck when drawing
                    if card.can_pay_cmc(self) and card.draw_amount < len(self.deck):
                        logger.info("played draw: " + card.get_name())
                        logger.info("draw amount: " + str(card.draw_amount))
                        # logger.info("deck left: " + str(len(self.deck)))
                        card.play(self)
                        logger.info("new hand: ")
                        logger.info(self.pretty_list(self.hand))
                        return

        # if not fogged, cast the cheapest draw so can pay fog later
        else:
            # sort hand by lowest cmc first
            self.sort_list_by_cmc_low_first(self.hand)
            for idx, card in enumerate(self.hand):
                if card.has_purpose('draw'):
                    if card.can_pay_cmc(self) and card.draw_amount <= len(self.deck):
                        logger.info("played draw: " + card.get_name())
                        card.play(self)
                        logger.info("new hand: ")
                        logger.info(self.pretty_list(self.hand))
                        return

    def can_cast_draw(self):
        can_cast_draw = False
        for card in self.hand:
            if card.has_purpose('draw'):
                # update draw amounts for cards like accumulated knowledge
                if card.has_purpose('draws more'):
                    card.update_draw_amount(self)
                if card.can_pay_cmc(self) and (card.draw_amount < len(self.deck)):
                    can_cast_draw = True
        return can_cast_draw
    
    def determine_and_cycle_land(self):
        hand_dict = self.get_card_counts(self.hand)
        if 'LorienRevealed' in hand_dict.keys():
            # only cycle lands if no lands in hand and less than 5 lands on battlefield
            should_cycle = True
            hand_type_dict = self.get_card_type_counts(self.hand)
            if 'land' in hand_type_dict.keys():
                should_cycle = False
            battlefield_type_dict = self.get_card_type_counts(self.battlefield)
            if 'land' in battlefield_type_dict.keys():
                if battlefield_type_dict['land'] > 5:
                    should_cycle = False
            
            if should_cycle:
                idx = self.find_card_index(self.hand, 'LorienRevealed')
                if self.hand[idx].can_cycle(self):
                    logger.info("land cycle " + self.hand[idx].get_name())
                    self.hand[idx].land_cycle(self)


    def determine_and_crack_fetch_land(self):
        mana_left = self.get_total_mana()
        basic_land_types = ['Island', 'Plains']
        
        # if there's no more mana, then no way to crack
        if mana_left == 0:
            return
        
        more_to_fetch = True
        
        while mana_left > 0 and more_to_fetch:
            battlefield_list = self.get_card_counts(self.battlefield)
            deck_list = self.get_card_counts(self.deck)
            # check if there are fetchlands to crack
            if 'Fetchland' not in battlefield_list:
                return
            
            lands_in_deck = {}
            land_to_fetch = None

            for basic_land in basic_land_types:
                # check if there are lands left to fetch
                lands_left_in_deck = 0
                if basic_land in deck_list.keys():
                    lands_left_in_deck = deck_list[basic_land] 
                lands_in_deck[basic_land] = lands_left_in_deck
            
            # if there's a plains then try to get island
            if 'Plains' in battlefield_list.keys():
                if lands_in_deck['Island'] > 0:
                    land_to_fetch = 'Island'
                elif lands_in_deck['Plains'] > 0:
                    land_to_fetch = 'Plains'
            else:
                if lands_in_deck['Plains'] > 0:
                    land_to_fetch = 'Plains'
                elif lands_in_deck['Island'] > 0:
                    land_to_fetch = 'Island'
            
            if land_to_fetch:
                logger.info('crack fetch for: ' + land_to_fetch)
                # logger.info(lands_in_deck)
                for idx, card in enumerate(self.battlefield):
                    if card.get_name() == 'Fetchland':
                        first_index = idx
                        break
                if self.battlefield[first_index].is_tapped():
                    self.battlefield[first_index].undo_tap(self)
                self.battlefield[first_index].crack_fetch_land(self, land_to_fetch)
            else:
                more_to_fetch = False

            mana_left -= 1     
        self.shuffle()
        return 
        

    def determine_card_to_discard(self):
        card_to_discard = None
        battlefield_card_type_dict = self.get_card_type_counts(self.battlefield)
        hand_type_dict = self.get_card_type_counts(self.hand)
        hand_dict = self.get_card_counts(self.hand)
        # logger.info("discard")
        # logger.info(self.pretty_list(self.hand))

        # check if there are two or more lands in hand
        if 'land' in hand_type_dict.keys():
            # don't need more than 2 lands in hand
            if hand_type_dict['land'] > 2:
                if 'Fetchland' in hand_dict.keys():
                    card_to_discard = 'Fetchland'
                    return card_to_discard
                elif 'Plains' in hand_dict.keys():
                    card_to_discard = 'Plains'
                    return card_to_discard
                else:
                    card_to_discard = 'Island'
                    return card_to_discard

        # check if there's enough lands
        if 'land' in battlefield_card_type_dict:
            lands_in_play = battlefield_card_type_dict['land']
            if lands_in_play > 4:
                if 'Fetchland' in hand_dict.keys():
                    card_to_discard = 'Fetchland'
                    return card_to_discard
                elif 'Plains' in hand_dict.keys():
                    card_to_discard = 'Plains'
                    return card_to_discard
                elif 'Island' in hand_dict.keys():
                    card_to_discard = 'Island'
                    return card_to_discard

        # else, discard the highest cmc card that isn't a wincon
        self.sort_list_by_cmc(self.hand)
        for i in range(len(self.hand)):
            card = self.hand[i]
            if not card.has_purpose('win con'):
                card_to_discard = card.get_name()
                return card_to_discard
            
        # if hand is all win con... then discard it
        if not card_to_discard:
            card_to_discard = self.hand[0].get_name()
            return card_to_discard

        assert card_to_discard != None

    def determine_play_any_land(self):
        for card in self.hand:
            if card.get_type() == 'land':
                self.play_land(card.get_name())
                logger.info('played land: ' + card.get_name())
                return

    def determine_and_play_land(self):
        # see what lands are in hand
        hand_dict = self.get_card_counts(self.hand)

        # check what mana is available first
        temp_mana_pool = {
            'w':0,
            'u':0,
            'b':0,
            'r':0,
            'g':0,
            'colorless':0
        }

        for card in self.battlefield:
            if card.get_type() == 'land':
                for color in card.generate_mana.keys():
                    temp_mana_pool[color] += card.generate_mana[color]

        land_to_play = None

        # if there's no white mana, play a white first
        if temp_mana_pool['w'] == 0:
            if 'Plains' in hand_dict.keys():
                land_to_play = 'Plains'
            elif 'Fetchland' in hand_dict.keys():
                land_to_play = 'Fetchland'
            elif 'Island' in hand_dict.keys():
                land_to_play = 'Island'
        elif temp_mana_pool['u'] < 2:
            if 'Island' in hand_dict.keys():
                land_to_play = 'Island'
            elif 'Fetchland' in hand_dict.keys():
                land_to_play = 'Fetchland'
            elif 'Plains' in hand_dict.keys():
                land_to_play = 'Plains'
        else:
            if 'Fetchland' in hand_dict.keys():
                land_to_play = 'Fetchland'
            elif 'Island' in hand_dict.keys():
                land_to_play = 'Island'
            elif 'Plains' in hand_dict.keys():
                land_to_play = 'Plains'

        if land_to_play:
            self.play_land(land_to_play)
            self.land_played_this_turn = True
            logger.info('played land: ' + land_to_play)

        return land_to_play
    
    ################ draw monarch
    def draw_if_monarch(self):
        if 'monarch' in self.status:
            self.draw(1)
            logger.info("draw for monarch")

    ################ campfire determinations
    def determine_tap_campfire_for_life(self):
        battlefield_dict = self.get_card_counts(self.battlefield)
        if 'Campfire' in battlefield_dict.keys():
            number_of_campfires = battlefield_dict['Campfire']
            for i in range(number_of_campfires):
                idx = self.get_first_untapped_on_battlefield('Campfire')
                if idx and self.get_total_mana() > 0:
                    self.battlefield[idx].tap_to_gain_life(self)
                    logger.info("campfire gained life")

    def determine_crack_campfire(self):
        # if there's no cards in deck, crack campfire if able
        battlefield_dict = self.get_card_counts(self.battlefield)
        if len(self.deck) < 2 and self.get_total_mana() >= 2:
            if 'Campfire' in battlefield_dict.keys():
                idx = self.get_first_untapped_on_battlefield('Campfire')
                self.battlefield[idx].shuffle_grave_to_library(self)
                logger.info("cracked campfire")

    #################### getting items

    def get_deck(self):
        return self.deck

    # get card counts of list
    def get_card_counts(self, search_list):
        result_dict = {}
        for card in search_list:
            card_name = card.get_name()
            # if already in key, add count
            if card_name in result_dict.keys():
                result_dict[card_name] += 1
            else:
                result_dict[card_name] = 1
        return result_dict
    
    def get_card_type_counts(self, search_list):
        result_dict = {}
        for card in search_list:
            type = card.get_type()
            # if already in key, add count
            if type in result_dict.keys():
                result_dict[type] += 1
            else:
                result_dict[type] = 1
        return result_dict
    
    def get_card_purpose_counts(self, search_list):
        result_dict = {}
        for card in search_list:
            purpose = card.get_purpose()
            # if already in key, add count
            if type in result_dict.keys():
                result_dict[purpose] += 1
            else:
                result_dict[purpose] = 1
        return result_dict

    def sort_list_by_cmc(self, search_list):
        search_list.sort(key=lambda x: x.get_cmc(), reverse=True)

    def sort_list_by_cmc_low_first(self, search_list):
        search_list.sort(key=lambda x: x.get_cmc())

    # gotta write a function instead of using remove
    def pop_item_by_card_name(self, list, card_name):
        for idx, card in enumerate(list):
            if card.get_name() == card_name:
                first_index = idx
                break
        return list.pop(first_index)

    def find_card_index(self, list, card_name):
        first_index = None
        for idx, card in enumerate(list):
            if card.get_name() == card_name:
                first_index = idx
                break
        return first_index
    
    def get_first_untapped_on_battlefield(self, card_name):
        first_index = None
        for idx, card in enumerate(self.battlefield):
            if card.get_name() == card_name:
                if not card.is_tapped():
                    first_index = idx
                    break
        return first_index
    
    ############################ setting status
    def set_fog(self):
        if 'fog' not in self.status:
            self.status.append('fog')
    
    def unset_fog(self):
        if 'fog' in self.status:
            self.status.remove('fog')

    def set_no_damage(self):
        if 'no damage' not in self.status:
            self.status.append('no damage')

    def unset_no_damage(self):
        if 'no damage' in self.status:
            self.status.remove('no damage')

    ############################# dmg profile
    # simple damage profile of 2 damage plus 2 a turn on no fogs
    def assign_dmg_from_opponent(self, turn):
        if 'no damage' in self.status:
            damage = 0
            self.fog_turns += 1
        elif 'fog' in self.status:
            damage = 2
            self.fog_turns += 1
        else:
            # damage = 2 + turn * 2 -4
            self.fog_missed += 1
            if turn > 3:
                damage = 100
            else:
                damage = 3
            if 'monarch' in self.status:
                self.status.remove('monarch')
                logger.info('lost monarch!')

        self.modify_life(-damage)

    ############################# for outputting
    def pretty_list(self, list):
        output_list = []
        for card in list:
            output_list.append(card.get_name())
        return output_list
    
