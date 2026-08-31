# Project Discussions

An [oTree](https://www.otree.org/) study that runs one leg of a deliberation experiment: participants form an opinion on a topic via an AI-led interview, get matched in real time with a disagreeing partner, are handed off to an external platform for an AI-facilitated discussion, and are brought back to fill out a post-discussion survey.

The discussion itself happens outside this codebase, on [deliberate-lab-extended](https://github.com/mgc93/deliberate-lab-extended) (a fork of Google's Deliberate Lab). This repo covers everything before and after that handoff: consent, the LLM interview, real-time matching, and the post-survey.

## Flow

```
Pre-Survey session (app_sequence: experiment_discussion -> experiment_matching)
  Consent -> Instructions -> InterviewTest -> TopicIntro -> LLMInterview
  -> OpinionPre -> AffectPre
  -> MatchingWait (paired by arrival time + opinion disagreement)
  -> PreDiscussionInstructions -> RedirectToDL  ---->  [ deliberate-lab-extended ]
                                                              |
Post-Survey session (app_sequence: experiment_post_survey)   v
  ManipulationCheck -> PostSurveyLanding -> OpinionPost -> ConversationSurvey
  -> PANASSurvey -> FacilitatorIntro -> FacilitatorSurvey -> FacilitatorPreference
  -> AffectSurvey -> AIAttitudes -> AIExperience -> AlgorithmicAversion
  -> OnlineExperience -> OpenFeedback -> BelievabilityCheck -> Debrief
  -> PostSurveyComplete
```

Participants leave oTree after `RedirectToDL`, complete the discussion on Deliberate Lab, and are redirected back into the `Post-Survey` oTree session (matched up via a participant code echoed through the URL) to finish up.

## Apps

- **`experiment_discussion/`** — Consent, instructions, a voice/text LLM interview (`LLMInterview.html`) that elicits the participant's stance on a randomly (or config-)selected topic, and pre-discussion opinion/affect measures. `creating_session` picks each participant's topic and experimental condition (facilitation style) up front.
- **`experiment_matching/`** — Pairs participants in real time. `group_by_arrival_time_method` matches waiting participants whose opinions differ by at least `DISAGREEMENT_THRESHOLD`, times out stragglers after `MATCH_TIMEOUT_MINUTES` (`EarlyReturn`), and hands matched pairs off to Deliberate Lab (`RedirectToDL`) by creating a cohort there via the API and redirecting with the participant's code, condition, and topic.
- **`experiment_post_survey/`** — Everything after the AI-facilitated discussion: manipulation checks, post-discussion opinion, conversation/facilitator ratings, PANAS affect scale, AI attitudes/experience, algorithmic aversion, open feedback, and debrief.

## Supporting modules

- **`llm_interview.py`** — Drives the pre-discussion interview: builds prompts from the selected topic, calls the Anthropic API (`ANTHROPIC_API_KEY`) to generate follow-up questions, and enforces `INTERVIEW_MAX_TURNS` / `INTERVIEW_TIMEOUT_SECONDS`.
- **`dl_api.py`** — Thin client for the Deliberate Lab (deliberate-lab-extended) backend API: creates cohorts/experiments and passes participants through, authenticated with `DL_API_KEY` against `DL_CONFIG['API_URL']`.
- **`discussion_topics.json`** — Bank of discussion topics (with metadata used by `TOPIC_FILTER`) that participants are assigned to.
- **`settings.py`** — oTree session configs, room definitions, the `DL_CONFIG` block (Deliberate Lab URLs/API key/per-condition experiment IDs, all read from environment variables), topic filtering, interview timing, and the opinion-distance/matching-timeout study parameters.
- **`codebook.Rmd`** — Analysis-side codebook documenting the exported variables for downstream (R) analysis.

## Data / dev artifacts

- **`data/`, `__temp_bots_*/`** — Exported session data (`all_apps_wide.csv`, `experiment_discussion.csv`, `experiment_matching.csv`) from bot test runs, not real participant data.
- **`db.sqlite3`** — Local oTree dev database.

## Configuration

Runtime secrets and environment-specific values (Anthropic API key, Deliberate Lab API URL/key/experiment IDs, oTree admin password/secret key, CloudResearch return URLs) are read from environment variables (see `settings.py`) via a local `.env` file, which is gitignored and not part of this repo.

## Running locally

```
pip install -r requirements.txt
otree devserver
```
