import card_classes.card_class as card

class AzureFleetAdmiral(card.Card):
    def __init__(self):
        super().__init__('AzureFleetAdmiral', 'creature', ['monarch'], 4, 0, 1, 0, 0, 0, 3)
        self.tapped = False

    def play(self, mtg_play):
        mtg_play.play_permanent(self.get_name())
        # set ability into status
        if 'monarch' not in mtg_play.status:
            mtg_play.status.append('monarch')
