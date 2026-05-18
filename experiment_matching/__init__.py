from otree.api import *
from settings import DL_CONFIG, MATCH_TIMEOUT_MINUTES, CLOUDRESEARCH_RETURN_URL, CLOUDRESEARCH_EARLY_RETURN_CODE


class C(BaseConstants):
    NAME_IN_URL = 'matching'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# ---------------------------------------------------------------------------
# Module-level matching function (must NOT be inside a class)
# ---------------------------------------------------------------------------

def group_by_arrival_time_method(subsession, waiting_players):
    from settings import DISAGREEMENT_THRESHOLD, DL_CONFIG
    from dl_api import create_dl_cohort

    # Only consider players who have submitted their post-interview opinion
    ready = [
        p for p in waiting_players
        if p.participant.opinion_pre is not None
        and not p.participant.is_matched
    ]

    for i, p1 in enumerate(ready):
        for p2 in ready[i + 1:]:
            diff = abs(p1.participant.opinion_pre - p2.participant.opinion_pre)
            if diff >= DISAGREEMENT_THRESHOLD:
                # Guard against exhausted queue
                if not subsession.session.condition_queue:
                    print("condition_queue is empty — cannot match pair")
                    return []

                # Peek at condition (do NOT pop yet — pop only on success)
                condition = subsession.session.condition_queue[0]

                # Create a dedicated 2-person cohort in DeliberateLab
                topic_statement = getattr(subsession.session, 'topic_statement', None)
                seed_message = f"{topic_statement} Please discuss!" if topic_statement else None
                try:
                    cohort_url = create_dl_cohort(condition, seed_message=seed_message)
                except Exception as e:
                    print(f"DL API error: {e}")
                    return []  # stop trying this round; retry on next arrival

                # API call succeeded — now consume the condition
                subsession.session.condition_queue.pop(0)

                # Assign to both participants
                for p in [p1, p2]:
                    p.participant.dl_url     = cohort_url
                    p.participant.condition  = condition
                    p.participant.is_matched = True

                subsession.session.pairs_matched += 1
                return [p1, p2]

    return []


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

class MatchingWait(WaitPage):
    group_by_arrival_time = True
    timeout_seconds       = 600

    @staticmethod
    def vars_for_template(player):
        return {
            'timeout_minutes': MATCH_TIMEOUT_MINUTES,
            'timeout_seconds': 600,
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened and not player.participant.is_matched:
            player.participant.is_dropout = True


class PreDiscussionInstructions(Page):
    @staticmethod
    def is_displayed(player):
        return not player.participant.is_dropout

    @staticmethod
    def vars_for_template(player):
        condition = player.participant.condition or ''
        return {'is_human_facilitator': condition.endswith('_human')}


class RedirectToDL(Page):
    @staticmethod
    def is_displayed(player):
        return not player.participant.is_dropout

    @staticmethod
    def vars_for_template(player):
        return {
            'dl_url':           player.participant.dl_url,
            'participant_code': player.participant.code,
            'topic_id':         player.session.topic_id,
            'condition':        player.participant.condition,
        }


class EarlyReturn(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.is_dropout

    @staticmethod
    def vars_for_template(player):
        return {
            'completion_code':         CLOUDRESEARCH_EARLY_RETURN_CODE,
            'completion_redirect_url': CLOUDRESEARCH_RETURN_URL,
        }


page_sequence = [
    MatchingWait,
    PreDiscussionInstructions,
    RedirectToDL,
    EarlyReturn,
]
