from __future__ import print_function
import mtg_play_class as mtg
import pandas as pd
import time
import logging
import sys

logger = logging.getLogger("turn_class")
# level = logging.INFO for all infos
logging.basicConfig(format='%(message)s', stream=sys.stdout, level=logging.CRITICAL)

# TODO, do an audit to see why it keeps subtracting islands

# make deck list
deck_dict = {
    ######## lands
    # 8 fetchland original
    'Fetchland':10,
    'Island':5,
    'Plains':5,

    ######### mill
    'Campfire':1,
    'JacesErasure':1,

    ######### monarch
    'AzureFleetAdmiral':2,

    ######### fogs
    'HolyDay':4,
    'DawnCharm':3,
    'EtherealHaze':4,
    'MomentOfSilence':1,
    'RiotControl':4,

    ######### draws
    'ArcaneDenial':4,
    'AccumulatedKnowledge':4,
    'Brainstorm':4,
    'KeepWatch':1,
    'UnionOfTheThirdPath':4,
    'WordsOfWisdom':2,
    'LorienRevealed':4
}


def play_with_deck(deck_dict):
    # initialize deck
    player = mtg.mtg_play(deck_dict)
    logger.info("deck size: " + str(len(player.deck)))

    # draw initial cards, maybe assuming no mulligan for now
    player.shuffle()
    player.draw(7)
    logger.info('Starting Hand: ')
    logger.info(player.pretty_list(player.hand))

    player.determine_and_mulligan()
    turn = 0

    turn_to_start_fogging = 3

    while (not player.lost) and (not player.win):
        turn += 1
    
        # untap
        player.untap_all()
        # upkeep
        player.upkeep()
        # draw
        player.draw(1)
        logger.info("Turn " + str(turn) + " *************************************")
        logger.info("life total: " + str(player.life))
        logger.info(player.pretty_list(player.hand))

        player.float_all_mana()
        # cycle lorien revealed if need be
        player.determine_and_cycle_land()

        # play land
            # how to determine what land to play
            # priortize to get at least one white for fog, then max blue
        player.determine_and_play_land()

        player.float_all_mana()

        # if there's no cards in deck, crack campfire if able
        player.determine_crack_campfire()

        if turn >= turn_to_start_fogging:
            # check if there's a fog in hand
            player.determine_and_play_fog()

            ### if have fog
            # play highest costing fog
            #### if less than 7 cards in hand --> play draw spell
            ### if don't have fog
            # play lowest costing draw spell, until fog in hand
            ## if no fog and no mana --> lose
            while ('fog' not in player.status) and (player.can_cast_draw()):
                player.determine_and_play_one_draw()
                player.determine_and_play_fog()

        # try to cast lifegain cards if < 5 life
        player.determine_and_play_lifegain()

        # try to cast win cons / mills
        player.determine_and_play_wincons()

        # try to get monarch
        player.determine_and_play_monarch()

        # cast more draws to get back to 7 cards if less than 7 cards
        player.determine_cast_more_draw_spells()

        # see if drew into lands and hadn't played lands yet
        if not player.land_played_this_turn:
            player.determine_play_any_land()
            player.float_all_mana()

        # determine whether to crack campfire here too, if last played
        player.determine_crack_campfire()

        # tap campfire to gain life if leftover mana
        player.determine_tap_campfire_for_life()

        # crack fetch lands if leftover mana
        player.determine_and_crack_fetch_land()

        # draw if monarch
        player.draw_if_monarch()

        # end step
        player.end_step()

        # set a damage profile and get prioritization to life gain when health low
        # simple one for now, 2 dmg a turn and 2 * turn dmg if no fog
        # may need to do different threat profiles, for terror, burn, elves, red aggro
        player.assign_dmg_from_opponent(turn)

    if player.lost:
        logger.info("lost at turn: " + str(turn))
    else:
        logger.info("won at turn: " + str(turn))
    logger.info("opponent milled: " + str(player.opponent_milled))
    logger.info("ending life total: " + str(player.life))
    logger.info("mulliganed times: " + str(player.mulligan_count))

    results_dict = {'win':player.win,
                    'end_turn': turn,
                    'opponent_milled':player.opponent_milled,
                    # 'ending_life':player.life,
                    # 'fog_turns':player.fog_turns,
                    # 'fogs_missed':player.fog_missed,
                    'mulligan_count':player.mulligan_count,
                    # 'end_deck_size':len(player.deck),
                    'lost_due_to_missed_fog':(not 'fog' in player.status)
                    }
    return results_dict

# optimize for win rate
def run_optimizer(deck_dict):
    original_deck = deck_dict.copy()

    types_of_lands = ['Island', 'Plains', 'Fetchland']
    optimized = False

    # for card in deck_dict.keys():
    card = 'Island'

    base_count = deck_dict[card]
    base_win_rate, avg_milled, lost_missed_fog, lost_burned = run_simulation(deck_dict)

    last_action = 'start'

    while not optimized:
        print('*************** optimizing: ' + card)

        # try adding or subtracing to see if the win rate increases
        # lands can have more than 4 copies
        one_more_copy = deck_dict[card] + 1
        one_less_copy = deck_dict[card] - 1

        if card not in types_of_lands:
            if one_more_copy > 4:
                one_more_copy = False
            if one_less_copy < 0:
                one_less_copy = False

        one_more_win_rate = 0
        one_less_win_rate = 0

        if one_more_copy and (last_action == 'start' or last_action == 'add'):
            deck_dict[card] = one_more_copy
            # simulate the one more and less to see if improves
            print(str(deck_dict[card]) + "  " + card)
            one_more_win_rate, avg_milled, lost_missed_fog, lost_burned = run_simulation(deck_dict)

        if one_less_copy and (last_action == 'start' or last_action == 'subtract'):
            deck_dict[card] = one_less_copy
            print(str(deck_dict[card]) + "  " + card)
            one_less_win_rate, avg_milled, lost_missed_fog, lost_burned = run_simulation(deck_dict)

        if base_win_rate > one_more_win_rate and base_win_rate > one_less_win_rate:
            deck_dict[card] = base_count
            optimized = True
            print('***************optimized :: ' + card + " " + str(base_count))

        else:
            if one_more_win_rate > base_win_rate:
                deck_dict[card] = one_more_copy
                one_less_copy = base_count
                one_less_win_rate = base_win_rate

                base_count = one_more_copy
                base_win_rate = one_more_win_rate

                last_action = 'add'
                print('adding one more')

            elif one_less_win_rate > base_win_rate:
                deck_dict[card] = one_less_copy
                one_more_copy = base_count
                one_more_win_rate = base_win_rate
                base_count = one_less_copy
                base_win_rate = one_less_win_rate
                last_action = 'subtract'
                print('subtracting one')

    # print new decklist
    for card in deck_dict.keys():
        print(str(deck_dict[card]) + "  " + card)



def run_simulation(deck_dict):
    sample_size = 50000
    result_list = []
    for i in range(sample_size):
        result_dict = play_with_deck(deck_dict)
        result_list.append(result_dict)
    df = pd.DataFrame(result_list)
    logger.info(df)

    # win_rate 
    win_rate = len(df.loc[df.win]) / len(df)
    avg_milled = df['opponent_milled'].mean()
    lost_missed_fog = len(df.loc[(df.win == False) & (df.lost_due_to_missed_fog == True) ]) / len(df)
    lost_burned = len(df.loc[(df.win == False) & (df.lost_due_to_missed_fog == False) ]) / len(df)
    mulligans_per_game = sum(df['mulligan_count']) / len(df)
    print('win rate: ' + str(win_rate))
    print('muligan rate: ' + str(mulligans_per_game))
    logger.info('avg milled: ' + str(avg_milled))
    print('lost missed fog: ' + str(lost_missed_fog))

    logger.info('lost burned: ' + str(lost_burned))
    return win_rate, avg_milled, lost_missed_fog, lost_burned

if __name__ == "__main__":
    print("start")
    start_time = time.time()
    # run_simulation(deck_dict)
    run_optimizer(deck_dict)
    print("--- %s seconds ---" % (time.time() - start_time))
