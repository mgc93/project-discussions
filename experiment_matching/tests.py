from otree.api import Bot, Submission
from . import EarlyReturn, PreDiscussionInstructions, RedirectToDL


class PlayerBot(Bot):
    def play_round(self):
        # MatchingWait is a WaitPage — oTree handles it automatically.

        if self.player.participant.is_dropout:
            yield Submission(EarlyReturn, check_html=False)
        else:
            yield Submission(PreDiscussionInstructions, check_html=False)
            yield Submission(RedirectToDL, check_html=False)
