from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'post_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    LIKERT_CHOICES = [1, 2, 3, 4, 5, 6, 7]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Linking fields — parsed from participant_label on arrival
    # participant_label format: "{pre_survey_code}___{topic_id}___{dl_public_id}___{cohort_name}"
    pre_survey_code = models.StringField(blank=True)
    dl_public_id    = models.StringField(blank=True)
    cohort_name     = models.StringField(blank=True)

    # Topic fields — looked up from discussion_topics.json using topic_id
    topic_id           = models.StringField(blank=True)
    topic_label        = models.StringField(blank=True)
    topic_statement    = models.StringField(blank=True)
    topic_category     = models.StringField(blank=True)
    topic_is_political = models.BooleanField(initial=False)
    topic_position_a   = models.StringField(blank=True)
    topic_position_b   = models.StringField(blank=True)

    # Post-discussion opinion
    opinion_post = models.IntegerField(min=0, max=100)

    # Conversation quality — 1–5 Likert (1 = Strongly disagree, 5 = Strongly agree)
    conv_productive          = models.IntegerField(min=1, max=5)  # Productivity
    conv_depth               = models.IntegerField(min=1, max=5)  # Depth
    conv_mutual_understanding= models.IntegerField(min=1, max=5)  # Mutual understanding
    conv_feeling_heard       = models.IntegerField(min=1, max=5)  # Feeling heard
    conv_good_faith          = models.IntegerField(min=1, max=5)  # Good faith
    conv_comfort             = models.IntegerField(min=1, max=5)  # Comfort
    conv_safety              = models.IntegerField(min=1, max=5)  # Safety (reverse-coded)
    conv_openness            = models.IntegerField(min=1, max=5)  # Openness

    # Affect & perceived distance — separate page
    affect_warmth       = models.IntegerField(min=0, max=100)  # feeling thermometer
    perceived_distance  = models.IntegerField(min=1, max=5)    # 1=very similar, 5=very different

    conv_future_engagement   = models.IntegerField(min=1, max=5)  # Future engagement
    conv_platform_willingness= models.IntegerField(min=1, max=5)  # Platform willingness

    # I-PANAS-SF (Thompson 2007) — 1=Very slightly or not at all, 5=Extremely
    panas_active      = models.IntegerField(min=1, max=5)  # Positive
    panas_determined  = models.IntegerField(min=1, max=5)  # Positive
    panas_attentive   = models.IntegerField(min=1, max=5)  # Positive
    panas_inspired    = models.IntegerField(min=1, max=5)  # Positive
    panas_alert       = models.IntegerField(min=1, max=5)  # Positive
    panas_afraid      = models.IntegerField(min=1, max=5)  # Negative
    panas_upset       = models.IntegerField(min=1, max=5)  # Negative
    panas_nervous     = models.IntegerField(min=1, max=5)  # Negative
    panas_ashamed     = models.IntegerField(min=1, max=5)  # Negative
    panas_hostile     = models.IntegerField(min=1, max=5)  # Negative

    # Facilitator evaluation — 1–5 Likert
    fac_warmth           = models.IntegerField(min=1, max=5)  # Trust – Warmth
    fac_competence       = models.IntegerField(min=1, max=5)  # Trust – Competence
    fac_legitimacy       = models.IntegerField(min=1, max=5)  # Legitimacy
    fac_fairness         = models.IntegerField(min=1, max=5)  # Procedural Fairness
    fac_appropriateness  = models.IntegerField(min=1, max=5)  # Appropriateness
    fac_timing           = models.IntegerField(min=1, max=5)  # Appropriateness of timing
    fac_intrusiveness    = models.IntegerField(min=1, max=5)  # Intrusiveness (reverse)
    fac_authenticity     = models.IntegerField(min=1, max=5)  # Authenticity
    fac_eff_understanding= models.IntegerField(min=1, max=5)  # Effectiveness – Understanding
    fac_eff_constructive = models.IntegerField(min=1, max=5)  # Effectiveness – Constructiveness
    fac_eff_civility     = models.IntegerField(min=1, max=5)  # Effectiveness – Civility
    fac_willingness      = models.IntegerField(min=1, max=5)  # Willingness to Participate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lookup_topic(topic_id: str) -> dict:
    import json, os
    json_path = os.path.join(os.path.dirname(__file__), '..', 'discussion_topics.json')
    with open(os.path.normpath(json_path), encoding='utf-8') as f:
        data = json.load(f)
    for t in data['topics']:
        if t['id'] == topic_id:
            return t
    return {}


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

class PostSurveyLanding(Page):
    """
    First page participants land on after DeliberateLab redirects them.

    Configure the DL completion URL as:
      https://your-otree.com/room/post_survey/?participant_label={EXTERNAL_ID}___{PARTICIPANT_ID}

    {EXTERNAL_ID} was set by oTree as "{participant.code}___{topic_id}", so the
    full participant_label on arrival is:
      "{pre_survey_code}___{topic_id}___{dl_public_id}"
    """

    @staticmethod
    def before_next_page(player, timeout_happened):
        label = player.participant.label or ''
        parts = label.split('___')

        player.pre_survey_code  = parts[0] if len(parts) > 0 else ''
        player.topic_id         = parts[1] if len(parts) > 1 else ''
        player.dl_public_id     = parts[2] if len(parts) > 2 else ''
        player.cohort_name      = parts[3] if len(parts) > 3 else ''

        # Look up full topic details
        topic = _lookup_topic(player.topic_id)
        player.topic_label        = topic.get('topic_label', '')
        player.topic_statement    = topic.get('statement', '')
        player.topic_category     = topic.get('category', '')
        player.topic_is_political = topic.get('is_political', False)
        player.topic_position_a   = topic.get('position_a', '')
        player.topic_position_b   = topic.get('position_b', '')

        # Mirror linking fields onto participant for easy export
        player.participant.pre_survey_code = player.pre_survey_code
        player.participant.dl_public_id    = player.dl_public_id
        player.participant.cohort_name     = player.cohort_name


class OpinionPost(Page):
    form_model  = 'player'
    form_fields = ['opinion_post']

    @staticmethod
    def vars_for_template(player):
        return {
            'topic_statement': player.topic_statement,
            'position_a':      player.topic_position_a,
            'position_b':      player.topic_position_b,
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.opinion_post = player.opinion_post


class ConversationSurvey(Page):
    form_model  = 'player'
    form_fields = [
        'conv_productive',
        'conv_depth',
        'conv_mutual_understanding',
        'conv_feeling_heard',
        'conv_good_faith',
        'conv_comfort',
        'conv_safety',
        'conv_openness',
        'conv_future_engagement',
        'conv_platform_willingness',
    ]

    @staticmethod
    def vars_for_template(player):
        return dict(questions=[
            dict(field='conv_productive',           construct='Productivity',          label='Overall, this was a productive conversation.',                              reverse=False),
            dict(field='conv_depth',                construct='Depth',                 label='We got beyond surface-level disagreement in this conversation.',            reverse=False),
            dict(field='conv_mutual_understanding', construct='Mutual understanding',  label="By the end, I felt I understood the other person's perspective.",           reverse=False),
            dict(field='conv_feeling_heard',        construct='Feeling heard',         label='The other person genuinely listened to what I had to say.',                 reverse=False),
            dict(field='conv_good_faith',           construct='Good faith',            label='The other person engaged with my arguments in good faith.',                 reverse=False),
            dict(field='conv_comfort',              construct='Comfort',               label='I felt comfortable expressing my views in this conversation.',               reverse=False),
            dict(field='conv_safety',               construct='Safety',                label='I was worried about being judged for what I said.',                         reverse=True),
            dict(field='conv_openness',              construct='Openness',              label='This conversation made me reconsider some of my views.',                              reverse=False),
            dict(field='conv_future_engagement',    construct='Future engagement',      label='I would be willing to have a similar conversation with someone who disagrees with me.', reverse=False),
            dict(field='conv_platform_willingness', construct='Platform willingness',   label='I would participate in another conversation on this platform.',                          reverse=False),
        ])


class PANASSurvey(Page):
    form_model  = 'player'
    form_fields = [
        'panas_active', 'panas_determined', 'panas_attentive', 'panas_inspired', 'panas_alert',
        'panas_afraid', 'panas_upset', 'panas_nervous', 'panas_ashamed', 'panas_hostile',
    ]

    @staticmethod
    def vars_for_template(player):
        return dict(items=[
            dict(field='panas_active',     label='Active'),
            dict(field='panas_determined', label='Determined'),
            dict(field='panas_attentive',  label='Attentive'),
            dict(field='panas_inspired',   label='Inspired'),
            dict(field='panas_alert',      label='Alert'),
            dict(field='panas_afraid',     label='Afraid'),
            dict(field='panas_upset',      label='Upset'),
            dict(field='panas_nervous',    label='Nervous'),
            dict(field='panas_ashamed',    label='Ashamed'),
            dict(field='panas_hostile',    label='Hostile'),
        ])


class FacilitatorSurvey(Page):
    form_model  = 'player'
    form_fields = [
        'fac_warmth',
        'fac_competence',
        'fac_legitimacy',
        'fac_fairness',
        'fac_appropriateness',
        'fac_timing',
        'fac_intrusiveness',
        'fac_authenticity',
        'fac_eff_understanding',
        'fac_eff_constructive',
        'fac_eff_civility',
        'fac_willingness',
    ]

    @staticmethod
    def vars_for_template(player):
        return dict(questions=[
            dict(field='fac_warmth',            construct='Trust – Warmth',                  label='The facilitator seemed warm and understanding.',                                     reverse=False),
            dict(field='fac_competence',         construct='Trust – Competence',              label='The facilitator understood the situation well.',                                     reverse=False),
            dict(field='fac_legitimacy',         construct='Legitimacy',                      label='This is the kind of intervention this facilitator should be allowed to make.',      reverse=False),
            dict(field='fac_fairness',           construct='Procedural Fairness',             label='The way the facilitator intervened was fair.',                                       reverse=False),
            dict(field='fac_appropriateness',    construct='Appropriateness',                 label='This intervention was appropriate for this situation.',                              reverse=False),
            dict(field='fac_timing',             construct='Appropriateness of timing',       label='The facilitator intervened at the right moment.',                                   reverse=False),
            dict(field='fac_intrusiveness',      construct='Intrusiveness',                   label="The facilitator's intervention felt disruptive to the conversation.",               reverse=True),
            dict(field='fac_authenticity',       construct='Authenticity',                    label="The facilitator's message felt genuine rather than scripted.",                      reverse=False),
            dict(field='fac_eff_understanding',  construct='Effectiveness – Understanding',   label='This intervention helped us understand each other better.',                         reverse=False),
            dict(field='fac_eff_constructive',   construct='Effectiveness – Constructiveness',label='This intervention made the conversation more productive.',                          reverse=False),
            dict(field='fac_eff_civility',       construct='Effectiveness – Civility',        label='This intervention improved the tone of the conversation.',                          reverse=False),
            dict(field='fac_willingness',        construct='Willingness to Participate',      label='I would participate in another conversation that used this kind of facilitator.',   reverse=False),
        ])


class AffectSurvey(Page):
    form_model  = 'player'
    form_fields = ['affect_warmth', 'perceived_distance']


class Debrief(Page):
    pass


class PostSurveyComplete(Page):
    @staticmethod
    def vars_for_template(_):
        from settings import CLOUDRESEARCH_RETURN_URL, CLOUDRESEARCH_COMPLETION_CODE
        return {
            'completion_code':         CLOUDRESEARCH_COMPLETION_CODE,
            'completion_redirect_url': CLOUDRESEARCH_RETURN_URL,
        }


page_sequence = [
    PostSurveyLanding,
    OpinionPost,
    ConversationSurvey,
    PANASSurvey,
    FacilitatorSurvey,
    AffectSurvey,
    Debrief,
    PostSurveyComplete,
]
