from otree.api import *
from settings import DL_CONFIG, TOPIC_FILTER, INTERVIEW_MAX_TURNS, INTERVIEW_TIMEOUT_SECONDS, INTERVIEW_VOICE_ONLY, INTERVIEW_TEST_VOICE_ONLY


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class C(BaseConstants):
    NAME_IN_URL = 'main'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    MAX_TURNS = INTERVIEW_MAX_TURNS  # hard cap; set INTERVIEW_MAX_TURNS in settings.py


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Stage 1 — Consent
    consent           = models.BooleanField(initial=False)
    cloudresearch_pid = models.StringField(label='CloudResearch Participant ID', blank=True)

    # Stage 2 — Voice test
    interview_test = models.LongStringField(blank=True)

    # Stage 3 — LLM interview
    conversation_json    = models.LongStringField(blank=True, initial='[]')
    current_answer       = models.LongStringField(blank=True)
    voice_answer         = models.LongStringField(blank=True)
    interview_transcript = models.LongStringField(blank=True)  # final serialised output

    # Stage 4 — Post-interview opinion
    opinion_pre = models.IntegerField(min=0, max=100)

    # Stage 5 — Affect toward opposing and same position
    affect_warmth_pre      = models.IntegerField(min=0, max=100)
    affect_warmth_pre_same = models.IntegerField(min=0, max=100)


# ---------------------------------------------------------------------------
# Session initialisation
# ---------------------------------------------------------------------------

def _select_topic(rng, pinned_id=None) -> dict:
    """Load discussion_topics.json, apply TOPIC_FILTER, return one random topic.

    If pinned_id is given (passed via session config), it takes precedence over
    TOPIC_FILTER and selects that specific topic directly.
    """
    import json, os

    json_path = os.path.join(os.path.dirname(__file__), '..', 'discussion_topics.json')
    with open(os.path.normpath(json_path), encoding='utf-8') as f:
        data = json.load(f)

    topics = data['topics']

    # Session-level pin takes priority over global TOPIC_FILTER
    if pinned_id is not None:
        topics = [t for t in topics if t['id'] == str(pinned_id)]
    else:
        if TOPIC_FILTER.get('topic_id') is not None:
            topics = [t for t in topics if t['id'] == str(TOPIC_FILTER['topic_id'])]
        if TOPIC_FILTER.get('is_political') is not None:
            topics = [t for t in topics if t['is_political'] == TOPIC_FILTER['is_political']]
        if TOPIC_FILTER.get('category') is not None:
            topics = [t for t in topics if t['category'] == TOPIC_FILTER['category']]

    if not topics:
        raise ValueError(
            f"No topic found for pinned_id={pinned_id!r} / TOPIC_FILTER={TOPIC_FILTER}. "
            "Check settings.py and discussion_topics.json."
        )

    return rng.choice(topics)


def creating_session(subsession: Subsession):
    import random, math

    rng = random.Random()

    # Select one topic for the whole session.
    # topic_id in session config takes priority over global TOPIC_FILTER.
    pinned_id = subsession.session.config.get('topic_id') or None
    topic = _select_topic(rng, pinned_id=pinned_id)
    s = subsession.session
    s.topic_id             = topic['id']
    s.topic_statement      = topic['statement']
    s.topic_label          = topic['topic_label']
    s.topic_category       = topic['category']
    s.topic_category_label = topic['category_label']
    s.topic_is_political   = topic['is_political']
    s.topic_position_a     = topic['position_a']
    s.topic_position_b     = topic['position_b']
    s.topic_ratings        = topic['ratings']

    # Initialise all participant fields so they are never missing downstream
    for player in subsession.get_players():
        p = player.participant
        p.opinion_pre          = None
        p.condition             = ''
        p.dl_url                = ''
        p.is_matched            = False
        p.is_dropout            = False
        p.interview_transcript  = ''

    conditions = list(DL_CONFIG['EXPERIMENTS'].keys())
    # Shuffle in blocks so each condition appears once per block of len(conditions)
    # dyads — guarantees near-perfect balance regardless of how many pairs form.
    n_repeats = math.ceil(subsession.session.num_participants / 2 / len(conditions)) + 5
    queue = []
    for _ in range(n_repeats):
        block = conditions[:]
        rng.shuffle(block)
        queue.extend(block)
    s.condition_queue = queue
    s.pairs_matched   = 0


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

class Consent(Page):
    form_model  = 'player'
    form_fields = ['consent', 'cloudresearch_pid']

    @staticmethod
    def error_message(player, values):
        if values['consent'] and not values['cloudresearch_pid']:
            return 'Please enter your CloudResearch Participant ID.'

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.consent:
            player.participant.cloudresearch_id = player.cloudresearch_pid


class NoConsent(Page):
    @staticmethod
    def is_displayed(player):
        return not player.consent


class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.consent


class InterviewTest(Page):
    form_model  = 'player'
    form_fields = ['interview_test']

    @staticmethod
    def vars_for_template(player):
        import os
        return dict(
            whisper_url=os.environ.get('WHISPER_URL', ''),
            whisper_token=os.environ.get('WHISPER_TOKEN', ''),
            voice_only=INTERVIEW_TEST_VOICE_ONLY,
        )


class TopicIntro(Page):
    @staticmethod
    def vars_for_template(player):
        return {'topic_label': player.session.topic_label}


class LLMInterview(Page):
    form_model  = 'player'
    form_fields = ['current_answer', 'voice_answer']

    @staticmethod
    def is_displayed(player):
        import time
        turns = player.participant.vars.get('interview_turns', 1)
        if turns > C.MAX_TURNS:
            return False
        if INTERVIEW_TIMEOUT_SECONDS is not None:
            start   = player.participant.vars.get('interview_start_time')
            elapsed = time.time() - start if start else 0
            if elapsed >= INTERVIEW_TIMEOUT_SECONDS:
                return False
        return True

    @staticmethod
    def vars_for_template(player):
        import json
        from datetime import datetime, timezone
        from llm_interview import get_opening_question

        import os, time as time_module
        if 'interview_turns' not in player.participant.vars:
            player.participant.vars['interview_turns'] = 1
        if 'interview_start_time' not in player.participant.vars:
            player.participant.vars['interview_start_time'] = time_module.time()

        current_turn = player.participant.vars['interview_turns']
        conversation = json.loads(player.conversation_json or '[]')

        # First turn: seed the opening question
        if not conversation:
            conversation.append({
                'question':      get_opening_question(player.session.topic_label, player.session.topic_is_political),
                'answer':        '',
                'time_sent':     datetime.now(timezone.utc).isoformat(),
                'time_received': None,
            })
            player.conversation_json = json.dumps(conversation)

        # Time remaining (None in rounds mode)
        if INTERVIEW_TIMEOUT_SECONDS is not None:
            elapsed        = time_module.time() - player.participant.vars['interview_start_time']
            time_remaining = max(0, int(INTERVIEW_TIMEOUT_SECONDS - elapsed))
        else:
            time_remaining = None

        return dict(
            conversation=conversation,
            current_turn=current_turn,
            max_turns=C.MAX_TURNS,
            progress_percentage=int(100 * current_turn / C.MAX_TURNS),
            time_remaining=time_remaining,
            timeout_mode=INTERVIEW_TIMEOUT_SECONDS is not None,
            voice_only=INTERVIEW_VOICE_ONLY,
            whisper_url=os.environ.get('WHISPER_URL', ''),
            whisper_token=os.environ.get('WHISPER_TOKEN', ''),
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        import json, time as time_module
        from datetime import datetime, timezone
        from llm_interview import generate_next_question, UserAnswer

        conversation = json.loads(player.conversation_json or '[]')
        current_turn = player.participant.vars.get('interview_turns', 1)

        # Record the answer for the current turn
        text_answer  = (player.current_answer or '').strip()
        voice_answer = (player.voice_answer   or '').strip()
        response     = text_answer or voice_answer or '[No response detected]'
        input_mode   = 'text' if text_answer else 'voice' if voice_answer else 'unknown'

        if conversation:
            conversation[-1]['answer']        = response
            conversation[-1]['input_mode']    = input_mode
            conversation[-1]['time_received'] = datetime.now(timezone.utc).isoformat()

        # Determine whether to generate a next question
        time_expired = False
        if INTERVIEW_TIMEOUT_SECONDS is not None:
            start        = player.participant.vars.get('interview_start_time', time_module.time())
            elapsed      = time_module.time() - start
            time_expired = elapsed >= INTERVIEW_TIMEOUT_SECONDS

        generate_next = current_turn < C.MAX_TURNS and not time_expired
        if generate_next:
            qa_history = [
                UserAnswer(question=e['question'], answer=e['answer'])
                for e in conversation
                if e.get('answer') and e['answer'].strip()
            ]
            next_question = generate_next_question(qa_history, n_rounds=C.MAX_TURNS, topic=player.session.topic_label, topic_statement=player.session.topic_statement)
            conversation.append({
                'question':  next_question,
                'answer':    '',
                'time_sent': datetime.now(timezone.utc).isoformat(),
            })

        player.conversation_json                = json.dumps(conversation)
        player.participant.vars['interview_turns'] = current_turn + 1

        # Always keep transcript up to date
        player.interview_transcript             = player.conversation_json
        player.participant.interview_transcript = player.conversation_json


class OpinionPre(Page):
    form_model  = 'player'
    form_fields = ['opinion_pre']

    @staticmethod
    def vars_for_template(player):
        s = player.session
        return {
            'topic_statement': s.topic_statement,
            'position_a':      s.topic_position_a,
            'position_b':      s.topic_position_b,
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.opinion_pre = player.opinion_pre


class AffectPre(Page):
    form_model  = 'player'
    form_fields = ['affect_warmth_pre', 'affect_warmth_pre_same']

    @staticmethod
    def vars_for_template(player):
        s = player.session
        if player.opinion_pre >= 50:
            opposing = s.topic_position_a
            same     = s.topic_position_b
        else:
            opposing = s.topic_position_b
            same     = s.topic_position_a
        return dict(opposing_position=opposing, same_position=same)


# ---------------------------------------------------------------------------
# Page sequence
# ---------------------------------------------------------------------------

page_sequence = (
    [Consent, NoConsent, Instructions, InterviewTest, TopicIntro]
    + [LLMInterview] * C.MAX_TURNS
    + [OpinionPre, AffectPre]
)
