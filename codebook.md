# Codebook: AI Facilitation Study

## Overview

This codebook covers all measured variables across three oTree apps:

| App | oTree name | Purpose |
|-----|-----------|---------|
| `experiment_discussion` | `main` | Consent, LLM interview, pre-discussion opinion |
| `experiment_matching` | `matching` | Wait page, condition assignment, DeliberateLab redirect |
| `experiment_post_survey` | `post_survey` | Post-discussion surveys (opinion, conversation, PANAS, facilitator, affect, AI attitudes, open feedback) |

**Export columns** follow the oTree wide-format convention:
`{app_name}.1.player.{field}` — e.g. `experiment_discussion.1.player.opinion_pre`

**Linking key across apps:**

| Field | Where stored | Description |
|-------|-------------|-------------|
| `participant.code` | oTree participant | Auto-generated oTree ID; used as `external_id` sent to DeliberateLab |
| `participant.label` | Post-survey participant | Set by DL redirect; format `{pre_code}___{topic_id}___{condition}___{dl_public_id}___{cohort_name}` |
| `cloudresearch_pid` | Pre-survey player | Self-reported CloudResearch ID entered on consent page |
| `dl_public_id` | Post-survey player | DeliberateLab anonymous participant ID (e.g. `hamster-yellow-3762`) |
| `pre_survey_code` | Post-survey player | oTree `participant.code` from the pre-survey session, recovered from DL redirect |

---

## Session-level variables

These are set once per session in `experiment_discussion` and available to all apps.

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `session.topic_id` | String | e.g. '001' | Unique topic ID from discussion_topics.json | |
| `session.topic_label` | String | — | Short topic label shown to participants | |
| `session.topic_statement` | String | — | Full topic statement used as discussion prompt | |
| `session.topic_category` | String | e.g. 'health_policy' | Topic category code | |
| `session.topic_category_label` | String | — | Human-readable category label | |
| `session.topic_is_political` | Boolean | TRUE / FALSE | Whether the topic is classified as political | |
| `session.topic_position_a` | String | — | Label for the left/low end of the opinion slider | |
| `session.topic_position_b` | String | — | Label for the right/high end of the opinion slider | |
| `session.pairs_matched` | Integer | ≥ 0 | Running count of successfully matched pairs in this session | |

---

## Participant-level fields

Stored on the oTree participant object; available in all apps via `participant.vars`.

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `participant.code` | String | Auto | oTree auto-generated participant ID; used as external_id in DL redirect | |
| `participant.cloudresearch_id` | String | — | CloudResearch participant ID entered on consent page | |
| `participant.condition` | String | 4 levels | Between-subjects condition assigned at matching | control_ai, control_human, bridging_ai, bridging_human |
| `participant.opinion_pre` | Integer | 0–100 | Pre-discussion opinion on the topic (0 = fully agree with position A, 100 = position B) | Collected in experiment_discussion |
| `participant.opinion_post` | Integer | 0–100 | Post-discussion opinion on the topic | Collected in experiment_post_survey |
| `participant.is_matched` | Boolean | TRUE/FALSE | Whether the participant was successfully matched with a partner | |
| `participant.is_dropout` | Boolean | TRUE/FALSE | Whether the participant timed out before being matched | |
| `participant.dl_url` | String | URL | Full DeliberateLab cohort URL assigned to this participant | |
| `participant.dl_public_id` | String | — | DeliberateLab anonymous participant ID recovered from post-survey redirect | |
| `participant.pre_survey_code` | String | — | oTree participant.code from the pre-survey, recovered from post-survey redirect | Links pre and post survey records |
| `participant.interview_transcript` | JSON String | — | Full LLM interview transcript as a JSON array of question–answer objects | |

---

## App 1: experiment_discussion

### Consent & identification

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_discussion.1.player.consent` | Boolean | TRUE / FALSE | Whether the participant provided informed consent | Participants who do not consent are redirected to a NoConsent page and do not proceed |
| `experiment_discussion.1.player.cloudresearch_pid` | String | — | CloudResearch participant ID as self-reported on consent page | Required only when consent = TRUE; copied to participant.cloudresearch_id |

### LLM interview

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_discussion.1.player.interview_test` | String | — | Text or transcription from the voice/microphone test page | |
| `experiment_discussion.1.player.conversation_json` | JSON String | — | Full interview conversation stored as a JSON array; updated after each turn | Each element: {question, answer, input_mode, time_sent, time_received} |
| `experiment_discussion.1.player.interview_transcript` | JSON String | — | Final copy of conversation_json saved at end of interview | Identical to conversation_json at completion; also mirrored to participant |

### Pre-discussion opinion

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_discussion.1.player.opinion_pre` | Integer | 0–100 | Participant's opinion on the discussion topic before the conversation (slider). 0 = fully agrees with position A; 100 = fully agrees with position B. | Mirrored to participant.opinion_pre for use in matching |

---

## App 2: experiment_matching

The matching app has **no player-level fields** in the database. All outcomes are stored on the participant object (see [Participant-level fields](#participant-level-fields) above).

### Condition assignment

Conditions are assigned at matching using a balanced shuffled queue. Each matched pair is assigned one condition.

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `participant.condition` | String | 4 levels | Between-subjects experimental condition assigned at matching | |

| Value | Facilitator | Strategy |
|---|---|---|
| control_ai | AI | Control (no active facilitation) |
| control_human | Human (confederate) | Control (no active facilitation) |
| bridging_ai | AI | Bridging intervention |
| bridging_human | Human (confederate) | Bridging intervention |

---

## App 3: experiment_post_survey

### Linking & topic fields

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.pre_survey_code` | String | — | oTree participant.code from the pre-survey session (links pre and post records) | Primary cross-session linking key |
| `experiment_post_survey.1.player.dl_public_id` | String | — | DeliberateLab anonymous participant ID | From DL completion redirect |
| `experiment_post_survey.1.player.topic_id` | String | — | Discussion topic ID (links to session topic fields) | |
| `experiment_post_survey.1.player.topic_label` | String | — | Short topic label | |
| `experiment_post_survey.1.player.topic_statement` | String | — | Full topic statement | |
| `experiment_post_survey.1.player.topic_category` | String | — | Topic category code | |
| `experiment_post_survey.1.player.topic_is_political` | Boolean | — | Whether the topic is political | |
| `experiment_post_survey.1.player.topic_position_a` | String | — | Left-end label of the opinion slider | |
| `experiment_post_survey.1.player.topic_position_b` | String | — | Right-end label of the opinion slider | |

### Manipulation check

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.manip_check_type` | String | 3 levels | Participant's belief about the type of facilitator they interacted with | ai_facilitator / human_facilitator / dont_remember |
| `experiment_post_survey.1.player.manip_check_confidence` | Integer | 1–5 | Confidence in the above answer (1 = not at all confident, 5 = very confident) | |

### Post-discussion opinion

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.opinion_post` | Integer | 0–100 | Participant's opinion on the discussion topic after the conversation (slider). 0 = fully agrees with position A; 100 = fully agrees with position B. | Mirrored to participant.opinion_post |

### Conversation quality (1–5 Likert)

Scale: 1 = Strongly disagree, 5 = Strongly agree.

| Variable | Type | Range | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.conv_satisfied` | Integer | 1–5 | Overall, I am satisfied with this conversation. | Overall satisfaction |
| `experiment_post_survey.1.player.conv_feeling_heard` | Integer | 1–5 | I felt heard and understood by my partner. | Feeling heard |
| `experiment_post_survey.1.player.conv_voice` | Integer | 1–5 | I was able to communicate my values and beliefs to my partner. | Voice / psychological safety |
| `experiment_post_survey.1.player.conv_understanding` | Integer | 1–5 | By the end, I felt I understood the other person's perspective. | Understanding the other person |
| `experiment_post_survey.1.player.conv_receptiveness` | Integer | 1–5 | The other person engaged with my arguments rather than dismissing them. | Good faith / receptiveness |
| `experiment_post_survey.1.player.conv_respect` | Integer | 1–5 | The other person treated me with respect. | Respect |
| `experiment_post_survey.1.player.conv_future_engage` | Integer | 1–5 | I would participate in another conversation on this platform. | Future engagement |

### I-PANAS-SF — Affect during conversation (1–5)

International Positive and Negative Affect Schedule — Short Form (Thompson, 2007).
Scale: 1 = Not at all, 5 = Extremely. Items presented in the order listed below.

| Variable | Type | Range | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.panas_upset` | Integer | 1–5 | Upset | Negative affect |
| `experiment_post_survey.1.player.panas_hostile` | Integer | 1–5 | Hostile | Negative affect |
| `experiment_post_survey.1.player.panas_alert` | Integer | 1–5 | Alert | Positive affect |
| `experiment_post_survey.1.player.panas_ashamed` | Integer | 1–5 | Ashamed | Negative affect |
| `experiment_post_survey.1.player.panas_inspired` | Integer | 1–5 | Inspired | Positive affect |
| `experiment_post_survey.1.player.panas_nervous` | Integer | 1–5 | Nervous | Negative affect |
| `experiment_post_survey.1.player.panas_determined` | Integer | 1–5 | Determined | Positive affect |
| `experiment_post_survey.1.player.panas_attentive` | Integer | 1–5 | Attentive | Positive affect |
| `experiment_post_survey.1.player.panas_afraid` | Integer | 1–5 | Afraid | Negative affect |
| `experiment_post_survey.1.player.panas_active` | Integer | 1–5 | Active | Positive affect |

### Facilitator evaluation (1–5 Likert)

Scale: 1 = Strongly disagree, 5 = Strongly agree. `fac_intrusiveness` is reverse-coded.

| Variable | Type | Range | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.fac_warmth` | Integer | 1–5 | The facilitator seemed warm and understanding. | Warmth |
| `experiment_post_survey.1.player.fac_competence` | Integer | 1–5 | The facilitator understood the situation well. | Competence |
| `experiment_post_survey.1.player.fac_legitimacy` | Integer | 1–5 | These are the kind of messages that this facilitator should be allowed to write. | Legitimacy |
| `experiment_post_survey.1.player.fac_fairness` | Integer | 1–5 | The way the facilitator intervened was fair. | Fairness |
| `experiment_post_survey.1.player.fac_intrusiveness` | Integer | 1–5 | The facilitator's intervention felt disruptive to the conversation. | Intrusiveness — reverse-coded |
| `experiment_post_survey.1.player.fac_eff_understanding` | Integer | 1–5 | This facilitator message would help the people in the conversation understand each other better. | Effectiveness – Understanding |
| `experiment_post_survey.1.player.fac_eff_civility` | Integer | 1–5 | This facilitator message would improve the tone of the conversation. | Effectiveness – Civility |
| `experiment_post_survey.1.player.fac_eff_constructive` | Integer | 1–5 | This intervention made the conversation more productive. | Effectiveness – Constructiveness |
| `experiment_post_survey.1.player.fac_willingness` | Integer | 1–5 | I would participate in a community that used this kind of facilitator. | Willingness to engage |

### Facilitator preference

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.pref_support` | Integer | 1–5 | I would support adding this kind of facilitator to real online platforms. | 1 = Strongly disagree, 5 = Strongly agree |
| `experiment_post_survey.1.player.pref_discussion` | String | 4 levels | For future discussions like this one, which type of facilitator would you prefer? | no_facilitator / human_facilitator / ai_facilitator / no_preference |

### Affect toward partner

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.affect_warmth` | Integer | 0–100 | Feeling thermometer: how warmly do you feel toward someone who holds the view expressed by the other participant? (0 = very cold/unfavourable, 50 = no feeling either way, 100 = very warm/favourable) | Feeling thermometer |

### Believability check (human-facilitator conditions only)

Only shown in `condition %in% c("control_human", "bridging_human")`.

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.human_fac_believability` | Integer | 1–5 | To what extent did you believe the facilitator messages were written by a real human being? | 1 = Not at all, 5 = Completely; blank for AI conditions |
| `experiment_post_survey.1.player.human_fac_suspicion` | String | 3 levels | At any point during the study, did you suspect that the human facilitator might actually be an AI? | yes / no / unsure; blank for AI conditions |

### GAAIS — General Attitudes towards AI Scale (1–5)

General Attitudes towards Artificial Intelligence Scale (Schepman & Rodway, 2020).
Scale: 1 = Strongly disagree, 5 = Strongly agree.

| Variable | Type | Range | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.gaais_pos_1` | Integer | 1–5 | For routine transactions, I would rather interact with an artificially intelligent system than with a human. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_2` | Integer | 1–5 | Artificial Intelligence can provide new economic opportunities for this country. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_3` | Integer | 1–5 | Artificially intelligent systems can help people feel happier. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_4` | Integer | 1–5 | I am impressed by what Artificial Intelligence can do. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_5` | Integer | 1–5 | I am interested in using artificially intelligent systems in my daily life. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_6` | Integer | 1–5 | Artificial Intelligence can have positive impacts on people's wellbeing. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_7` | Integer | 1–5 | Artificial Intelligence is exciting. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_8` | Integer | 1–5 | An artificially intelligent agent would be better than an employee in many routine jobs. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_9` | Integer | 1–5 | There are many beneficial applications of Artificial Intelligence. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_10` | Integer | 1–5 | Artificially intelligent systems can perform better than humans. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_11` | Integer | 1–5 | Much of society will benefit from a future full of Artificial Intelligence. | Positive subscale |
| `experiment_post_survey.1.player.gaais_pos_12` | Integer | 1–5 | I would like to use Artificial Intelligence in my own job. | Positive subscale |
| `experiment_post_survey.1.player.gaais_neg_1` | Integer | 1–5 | Organisations use Artificial Intelligence unethically. | Negative subscale |
| `experiment_post_survey.1.player.gaais_neg_2` | Integer | 1–5 | I think artificially intelligent systems make many errors. | Negative subscale |
| `experiment_post_survey.1.player.gaais_neg_3` | Integer | 1–5 | I find Artificial Intelligence sinister. | Negative subscale |
| `experiment_post_survey.1.player.gaais_neg_4` | Integer | 1–5 | Artificial Intelligence might take control of people. | Negative subscale |
| `experiment_post_survey.1.player.gaais_neg_5` | Integer | 1–5 | I think Artificial Intelligence is dangerous. | Negative subscale |
| `experiment_post_survey.1.player.gaais_neg_6` | Integer | 1–5 | I shiver with discomfort when I think about future uses of Artificial Intelligence. | Negative subscale |
| `experiment_post_survey.1.player.gaais_neg_7` | Integer | 1–5 | People like me will suffer if Artificial Intelligence is used more and more. | Negative subscale |
| `experiment_post_survey.1.player.gaais_neg_8` | Integer | 1–5 | Artificial Intelligence is used to spy on people. | Negative subscale |

### AI experience

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.ai_familiarity` | String | 5 levels | How familiar are you with AI chatbots (like ChatGPT, Claude, Gemini)? | not_at_all / slightly / moderately / very / extremely |
| `experiment_post_survey.1.player.ai_usage_frequency` | String | 5 levels | How often do you use AI tools (chatbots, AI assistants, AI-generated content)? | never / less_than_monthly / monthly / weekly / daily |
| `experiment_post_survey.1.player.ai_moderation_encountered` | String | 3 levels | Have you knowingly encountered AI-powered moderation or facilitation online? | yes / no / not_sure |
| `experiment_post_survey.1.player.ai_use_advice` | Boolean | TRUE/FALSE | AI use: getting advice or recommendations on personal matters | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.ai_use_emotional` | Boolean | TRUE/FALSE | AI use: emotional support or discussing feelings/problems | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.ai_use_casual` | Boolean | TRUE/FALSE | AI use: casual conversation or companionship | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.ai_use_writing` | Boolean | TRUE/FALSE | AI use: writing or editing text | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.ai_use_coding` | Boolean | TRUE/FALSE | AI use: coding or technical tasks | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.ai_use_research` | Boolean | TRUE/FALSE | AI use: research or fact-checking | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.ai_use_creative` | Boolean | TRUE/FALSE | AI use: creative projects or entertainment | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.ai_use_learning` | Boolean | TRUE/FALSE | AI use: learning new topics or skills | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.ai_use_none` | Boolean | TRUE/FALSE | Has not used AI chatbots for any of the listed purposes | Checkbox — blank=True if unchecked |

### Algorithmic aversion (1–5 Likert)

Scale: 1 = Strongly disagree, 5 = Strongly agree.

| Variable | Type | Range | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.algo_aversion_1` | Integer | 1–5 | I generally prefer human facilitators over AI facilitators in online discussions. | |
| `experiment_post_survey.1.player.algo_aversion_2` | Integer | 1–5 | I would trust a human more than an AI to handle conflicts fairly in online conversations. | |
| `experiment_post_survey.1.player.algo_aversion_3` | Integer | 1–5 | I feel more comfortable when humans, rather than AI, moderate online discussions. | |

### Online discussion experience

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.discuss_frequency` | String | 5 levels | How often do you participate in online discussions about current events or social issues? | never / a_few_times_a_year / a_few_times_a_month / a_few_times_a_week / every_day |
| `experiment_post_survey.1.player.discuss_platform_facebook` | Boolean | TRUE/FALSE | Platform: Facebook | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.discuss_platform_youtube` | Boolean | TRUE/FALSE | Platform: YouTube | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.discuss_platform_whatsapp` | Boolean | TRUE/FALSE | Platform: WhatsApp | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.discuss_platform_instagram` | Boolean | TRUE/FALSE | Platform: Instagram | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.discuss_platform_other` | Boolean | TRUE/FALSE | Platform: Other | Checkbox — blank=True if unchecked |
| `experiment_post_survey.1.player.discuss_platform_other_text` | String | — | Free-text description of other platform(s) used | Only filled if discuss_platform_other = TRUE |
| `experiment_post_survey.1.player.discuss_content_removed` | String | yes/no | Has any of your online content ever been removed or flagged by a moderator? | |
| `experiment_post_survey.1.player.discuss_is_moderator` | String | yes/no | Have you ever been a moderator or administrator of an online community? | |
| `experiment_post_survey.1.player.discuss_witness_conflicts` | String | 5 levels | How often do you witness conflicts or heated arguments in online discussions? | never / a_few_times_a_year / a_few_times_a_month / a_few_times_a_week / every_day |

### Open feedback

| Variable | Type | Range / Values | Description | Notes |
|---|---|---|---|---|
| `experiment_post_survey.1.player.feedback_topic` | String | — | Open-text feedback about the discussion topic | Optional; blank=True |
| `experiment_post_survey.1.player.feedback_conversation` | String | — | Open-text feedback about the conversation experience | Optional; blank=True |
| `experiment_post_survey.1.player.feedback_facilitators` | String | — | Open-text feedback about the facilitators | Optional; blank=True |

---

## Notes on reverse-coding

The following item should be reverse-coded before computing scale scores:

| Variable | Item | Formula |
|---|---|---|
| `fac_intrusiveness` | The facilitator's intervention felt disruptive to the conversation. | `fac_intrusiveness_r = 6 - fac_intrusiveness` |

---

## References

Schepman, A., & Rodway, P. (2020). Initial validation of the General Attitudes towards Artificial Intelligence Scale. *Computers in Human Behavior Reports, 1*, 100014.

Thompson, E. R. (2007). Development and validation of an internationally reliable short-form of the Positive and Negative Affect Schedule (PANAS). *Journal of Cross-Cultural Psychology, 38*(2), 227–242.
