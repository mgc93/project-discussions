# Core LLM logic adapted from:
# https://github.com/victor-m-p/beliefs-narratives-networks/blob/main/otreesurvey/otreesurvey_app/llm_adaptive.py
# UserAnswer, InterviewTurn, and retry logic copied directly.
# call_openai replaced with call_anthropic (Anthropic Messages API + tool use
# for structured output). generate_next_question adapts
# generate_conversational_question with a topic-agnostic placeholder prompt.
# Replace [TOPIC PLACEHOLDER] and the four [COVERAGE GOAL] items before running.

import anthropic
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

custom_retry = retry(
        stop=stop_after_attempt(5),      # Number of retries (change as needed)
        wait=wait_fixed(2),              # Wait 2 seconds between retries
        reraise=True                     # Raise the exception if all retries fail
        )


@custom_retry
def call_anthropic(response_model, content_prompt, model_name='claude-sonnet-4-6', max_tokens=1024):
    """
    Calls the Anthropic Messages API and returns a validated Pydantic instance.
    Structured output is achieved via tool use (tool_choice='any'), which forces
    the model to return a JSON object matching the Pydantic model's schema.
    """
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    # Derive a JSON-schema tool from the Pydantic model
    schema    = response_model.model_json_schema()
    tool_name = response_model.__name__

    tools = [{
        "name":         tool_name,
        "description":  f"Structured output for {tool_name}",
        "input_schema": schema,
    }]

    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": content_prompt}],
        )
    except Exception as exc:
        print(f"Exception with model {model_name}: {exc}")
        raise

    for block in response.content:
        if block.type == "tool_use":
            return response_model(**block.input)

    raise ValueError(f"No tool_use block in Anthropic response for {tool_name}")


class UserAnswer(BaseModel):
    question: str
    answer: str


class InterviewTurn(BaseModel):
    interviewer_utterance: str = Field(
        ...,
        description="The interviewer's utterance, containing acknowledgment of "
                    "the previous answer and a relevant follow-up question.",
    )
    rationale: Optional[str] = Field(
        None,
        description="Short rationale explaining why this utterance is appropriate "
                    "given the context.",
    )


def get_opening_question(topic_label: str, is_political: bool) -> str:
    if is_political:
        return (
            f"We're going to talk about {topic_label}. Before getting into the debate itself, "
            f"I'm curious — is this something you've thought about before, or is it "
            f"relatively new to you?"
        )
    else:
        return (
            f"We're going to talk about {topic_label}. Is this something that comes up in your "
            f"own life, or is it more of an abstract question for you?"
        )


def generate_next_question(history: list[UserAnswer], n_rounds: int = 8, topic: str = '') -> str:
    """
    Adapted from generate_conversational_question in llm_adaptive.py (victor-m-p).
    Replace the four [COVERAGE GOAL] items before running.
    """
    conversation_str = ""
    for turn in history:
        conversation_str += f"Interviewer: {turn.question}\nParticipant: {turn.answer}\n\n"

    current_round = len(history) + 1

    # RESEARCHER: Replace each [COVERAGE GOAL N] with one concrete learning objective.
    system_prompt = f"""
Context:
You are a thoughtful, empathetic, and curious interviewer exploring {topic} with an interviewee.

Current conversation:
{conversation_str}

=*=*=

Task Description:
Interview objective: By the end of the conversation, the interviewer has to learn about the following:
1) The participant's personal stance on the topic and the core values or 
   principles that underlie it.
2) The specific reasons, experiences, or pieces of evidence that have 
   shaped or reinforced their view.
3) Tensions, uncertainties, or considerations they find genuinely difficult 
   to resolve — including arguments from the other side they find compelling.
4) How people close to them (friends, family, community) tend to think about 
   the topic, and whether that has influenced their own view.

Follow this strategy to generate your next question:
1) Assess which of the 4 coverage goals have been adequately addressed so far, and which ones still need more exploration.
2.1) If the previous answer introduced something potentially (1) important, (2) interesting, or (3) unclear, formulate an elaboration question about this.
2.2) Otherwise, prefer asking about an uncovered goal from the list above.
2.3) If one of the interview goals above is not important for the participant do not pursue it further.
2.4) If the participant has stated a belief without explaining *why* they 
     hold it, ask them to elaborate on the reasoning or experience behind it 
     before moving to a new coverage goal.
3) For the second-to-last question, ask the participant whether any of the 
   things they have mentioned feel connected or in tension with each other.
   For the final question, invite them to share anything important that has 
   not come up.

Follow these guidelines when constructing your next question:
1) Acknowledge the participant's last answer to show you are listening and value their input.
2) Respond naturally to what the participant has said: be curious, warm and non-judgmental.
3) Ask one focused open question per turn (avoid asking about more than one thing and avoid leading phrasing).
4) Keep it concise: ~1 sentence acknowledging what they said, then 1 clear question.
5) Avoid moralizing, advice, assumptions, checklists, multiple-choice, or multi-part questions.
6) When a participant gives a reason for their view, ask about the reason 
   itself — not just to confirm they hold it, but to understand where it 
   comes from.

Safety note: In an extreme case where the interviewee *explicitly* refuses to answer, do not force them. Instead move the interview forward by asking about another topic from the list above.

Conversation constraints:
- You have {n_rounds} total turns; this is round {current_round} of {n_rounds}.

Based on the current conversation generate the next interviewer question that best follows the strategy and guidelines above.
"""

    result = call_anthropic(
        response_model=InterviewTurn,
        content_prompt=system_prompt,
        model_name='claude-sonnet-4-6',
    )
    return result.interviewer_utterance
