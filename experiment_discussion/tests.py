from otree.api import Bot, Submission
from . import C, Consent, Instructions, InterviewTest, TopicIntro, LLMInterview, OpinionPre


class PlayerBot(Bot):
    def play_round(self):
        # Give the two bots opinions far enough apart to trigger matching
        # (threshold = 20; bot 1 → 15, bot 2 → 85, diff = 70)
        opinion_pre = 15 if self.player.id_in_subsession % 2 == 1 else 85

        yield Submission(Consent, {'consent': True, 'cloudresearch_pid': 'TEST123'}, check_html=False)

        yield Submission(Instructions, check_html=False)

        yield Submission(InterviewTest, {'interview_test': 'Test transcript'}, check_html=False)

        yield Submission(TopicIntro, check_html=False)

        # One submission per interview turn (no LLM called — answers go straight
        # to before_next_page which skips question generation for bots)
        for i in range(C.MAX_TURNS):
            yield Submission(LLMInterview, {
                'current_answer': f'Mock answer {i + 1}',
                'voice_answer':   '',
            }, check_html=False)

        yield Submission(OpinionPre, {'opinion_pre': opinion_pre}, check_html=False)
