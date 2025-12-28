import mtg_play_class as mtg

def main():
    # make deck list
    deck_dict = {
        ######## lands
        'Island':5,
        'Plains':5,
        'Fetchland':8,

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
        'LorienRevealed':4,

        ######### mill
        'Campfire':1,
        'JacesErasure':1,

        ######### monarch
        'AzureFleetAdmiral':2
    }

    # initialize deck
    player = mtg.mtg_play(deck_dict)
    print("deck size: " + str(len(player.deck)))

    # draw initial cards, maybe assuming no mulligan for now
    player.shuffle()
    player.draw(7)
    print('Starting Hand: ')
    print(player.pretty_list(player.hand))

    # assume no mulligan for now
    turn = 1

    turn_to_start_fogging = 3

    while (not player.lost) and (not player.win):
    
        # untap
        player.untap_all()
        # upkeep
        player.upkeep()
        # draw
        player.draw(1)
        print("Turn " + str(turn) + " *************************************")
        print("life total: " + str(player.life))
        turn += 1
        print(player.pretty_list(player.hand))

        # cycle lorien revealed if need be
        player.determine_and_cycle_land()

        # play land
            # how to determine what land to play
            # priortize to get at least one white for fog, then max blue
        player.determine_and_play_land()

        player.float_all_mana()

        # if there's no cards in deck, crack campfire if able
        player.determine_crack_campfire()

        if turn > turn_to_start_fogging:
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
        print("lost at turn: " + str(turn))
    else:
        print("won at turn: " + str(turn))
    print("opponent milled: " + str(player.opponent_milled))
    print("ending life total: " + str(player.life))
    print("mulliganed times: " + str(player.mulligan_count))


if __name__ == "__main__":
    main()
