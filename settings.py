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
        topic_id='',     # set to a topic ID string (e.g. '001') when creating a session
        # Relative weights for condition assignment (set to 0 to exclude a condition).
        # These are editable per-session in the oTree admin "Create session" UI.
        prop_bridging_ai=6,
        prop_control_ai=4,
        prop_descriptive_norm_ai=16,
        prop_emotional_validation_ai=4,
        prop_neutral_summarization_ai=0,
        prop_confidence_calibration_ai=0,
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
    'cohort_name',           # str — DeliberateLab cohort name, echoed back in completion redirect
    'matching_start_time',   # float — unix timestamp when participant first hit MatchingWait
]

# ---------------------------------------------------------------------------
# DeliberateLab API configuration
# ---------------------------------------------------------------------------
DL_CONFIG = {
    'API_URL':      os.environ.get('DL_API_URL', ''),       # backend: us-central1-*.cloudfunctions.net
    'FRONTEND_URL': os.environ.get('DL_FRONTEND_URL', ''),  # frontend: exp-discussion.web.app
    'API_KEY':      os.environ.get('DL_API_KEY', ''),
    'EXPERIMENTS': {
        'control_ai':                 os.environ.get('DL_EXP_ID_CONTROL_AI', ''),
        'bridging_ai':                os.environ.get('DL_EXP_ID_BRIDGING_AI', ''),
        'neutral_summarization_ai':   os.environ.get('DL_EXP_ID_NEUTRAL_SUMMARIZATION_AI', ''),
        'emotional_validation_ai':    os.environ.get('DL_EXP_ID_EMOTIONAL_VALIDATION_AI', ''),
        'descriptive_norm_ai':        os.environ.get('DL_EXP_ID_DESCRIPTIVE_NORM_AI', ''),
        'confidence_calibration_ai':  os.environ.get('DL_EXP_ID_CONFIDENCE_CALIBRATION_AI', ''),
    },
}

# ---------------------------------------------------------------------------
# Participant panel return / completion codes
# ---------------------------------------------------------------------------
CLOUDRESEARCH_RETURN_URL        = os.environ.get('CLOUDRESEARCH_RETURN_URL', '')
CLOUDRESEARCH_COMPLETION_CODE   = os.environ.get('CLOUDRESEARCH_COMPLETION_CODE', '')
CLOUDRESEARCH_EARLY_RETURN_URL  = os.environ.get('CLOUDRESEARCH_EARLY_RETURN_URL', '')
CLOUDRESEARCH_EARLY_RETURN_CODE = os.environ.get('CLOUDRESEARCH_EARLY_RETURN_CODE', '')

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
INTERVIEW_MAX_TURNS = 10         # hard cap on number of questions
INTERVIEW_TIMEOUT_SECONDS = 720  # 720s = 12 minutes; interview ends at whichever comes first
INTERVIEW_VOICE_ONLY      = False   # True = voice input only; False = voice preferred but text allowed
INTERVIEW_TEST_VOICE_ONLY = True   # Same setting for the voice test page

# ---------------------------------------------------------------------------
# Study parameters
# ---------------------------------------------------------------------------
DISAGREEMENT_THRESHOLD = 38   # minimum opinion distance to form a pair
MATCH_TIMEOUT_MINUTES  = 10   # how long participants wait before dropout

# ---------------------------------------------------------------------------
# Standard oTree settings
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False
ROOMS = [
    # Pre-survey rooms — one per topic you want to run simultaneously.
    # When creating a session for a room, set topic_id in the session config
    # (e.g. topic_id='001') to pin that room to a specific discussion topic.
    dict(name='pre_survey_1', display_name='Pre-Survey — Room 1'),
    dict(name='pre_survey_2', display_name='Pre-Survey — Room 2'),
    dict(name='pre_survey_3', display_name='Pre-Survey — Room 3'),
    dict(name='pre_survey_4', display_name='Pre-Survey — Room 4'),
    dict(name='pre_survey_5', display_name='Pre-Survey — Room 5'),
    dict(name='pre_survey_6', display_name='Pre-Survey — Room 6'),
    # Post-survey room — shared across all topics
    dict(
        name='post_survey',
        display_name='Post-Survey Room',
    ),
]
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = os.environ.get('OTREE_ADMIN_PASSWORD', 'otree')
SECRET_KEY = os.environ.get('OTREE_SECRET_KEY', 'change-me-in-production')
DEBUG = os.environ.get('OTREE_PRODUCTION', '') == ''
