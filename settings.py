import os
from dotenv import load_dotenv

load_dotenv()

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
)

SESSION_CONFIGS = [
    dict(
        name='pre_survey',
        display_name='Pre-Survey',
        app_sequence=['experiment_discussion', 'experiment_matching'],
        num_demo_participants=2,
    ),
    dict(
        name='post_survey',
        display_name='Post-Survey',
        app_sequence=['experiment_post_survey'],
        num_demo_participants=2,
    ),
]

SESSION_FIELDS = [
    'condition_queue',        # list[str] — balanced shuffle of condition names
    'pairs_matched',          # int — running count of matched pairs
    # Selected discussion topic (set once in creating_session)
    'topic_id',               # str
    'topic_statement',        # str
    'topic_label',            # str
    'topic_category',         # str
    'topic_category_label',   # str
    'topic_is_political',     # bool
    'topic_position_a',       # str
    'topic_position_b',       # str
    'topic_ratings',          # dict
]

PARTICIPANT_FIELDS = [
    'opinion_pre',           # float — pre-discussion opinion (collected in experiment_discussion)
    'opinion_post',          # float — post-discussion opinion (collected in experiment_post_survey)
    'condition',             # str
    'dl_url',                # str
    'is_matched',            # bool
    'is_dropout',            # bool
    'interview_transcript',  # str
    'cloudresearch_id',      # str — entered by participant on consent page
    'dl_public_id',          # str — DeliberateLab anonymous ID (e.g. hamster-yellow-3762)
    'pre_survey_code',       # str — oTree participant code from pre-survey, echoed back by DL
]

# ---------------------------------------------------------------------------
# DeliberateLab API configuration
# ---------------------------------------------------------------------------
DL_CONFIG = {
    'API_URL':      os.environ.get('DL_API_URL', ''),       # backend: us-central1-*.cloudfunctions.net
    'FRONTEND_URL': os.environ.get('DL_FRONTEND_URL', ''),  # frontend: exp-discussion.web.app
    'API_KEY':      os.environ.get('DL_API_KEY', ''),
    'EXPERIMENTS': {
        'control_ai':    os.environ.get('DL_EXP_ID_CONTROL_AI', ''),
        'control_human': os.environ.get('DL_EXP_ID_CONTROL_HUMAN', ''),
        'bridging_ai':   os.environ.get('DL_EXP_ID_BRIDGING_AI', ''),
        'bridging_human':os.environ.get('DL_EXP_ID_BRIDGING_HUMAN', ''),
    },
}

# ---------------------------------------------------------------------------
# Participant panel return / completion codes
# ---------------------------------------------------------------------------
CLOUDRESEARCH_RETURN_URL       = os.environ.get('CLOUDRESEARCH_RETURN_URL', '')
CLOUDRESEARCH_COMPLETION_CODE  = os.environ.get('CLOUDRESEARCH_COMPLETION_CODE', '')

# ---------------------------------------------------------------------------
# Discussion topic selection
# ---------------------------------------------------------------------------
# Set a value to filter; leave as None to skip that filter.
# All three filters are ANDed together.
TOPIC_FILTER = {
    'is_political': None,   # True / False / None (no filter)
    'category':     None,   # e.g. 'health_policy' / None (no filter)
    'topic_id':     None,   # e.g. '001' to pin a specific topic / None (random)
}

# ---------------------------------------------------------------------------
# Interview configuration
# ---------------------------------------------------------------------------
INTERVIEW_MAX_TURNS = 0          # 0 = skip interview entirely; set to 8 for production
INTERVIEW_TIMEOUT_SECONDS = 0   # None → rounds mode (exactly MAX_TURNS questions)
                                   # e.g. 900 → timeout mode (15 min total, MAX_TURNS as ceiling)

# ---------------------------------------------------------------------------
# Study parameters
# ---------------------------------------------------------------------------
DISAGREEMENT_THRESHOLD = 20   # minimum opinion distance to form a pair
MATCH_TIMEOUT_MINUTES  = 10   # how long participants wait before dropout

# ---------------------------------------------------------------------------
# Standard oTree settings
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False
ROOMS = [
    dict(
        name='post_survey',
        display_name='Post-Survey Room',
        # No participant_label_file — open room, any participant_label accepted
    ),
]
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = os.environ.get('OTREE_ADMIN_PASSWORD', 'otree')
SECRET_KEY = os.environ.get('OTREE_SECRET_KEY', 'change-me-in-production')
DEBUG = os.environ.get('OTREE_PRODUCTION', '') == ''
