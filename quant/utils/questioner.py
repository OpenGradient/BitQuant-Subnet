from datetime import timedelta, datetime
from typing import Optional
import random
import json

import google.genai as genai
from pydantic import BaseModel, Field
import bittensor as bt


GENERATION_PROMPT = """Create a list of {question_count} questions that sound like they're being asked by a real person with varying levels of knowledge. The questions should be about common crypto topics. Some should be professionally formatted and others lazy (e.g., no capitalization, missing punctuation). The questions should cover the following topics, with an example for each:
* Portfolio Analytics: (e.g., "how can i evaluate my portfolio risk")
* Yield & Earning: (e.g., "what's the best way to earn yield on my ETH")
* Trading & Popularity: (e.g., "what are the trading tokens on solana?")
* Investment Advice: (e.g., "should i buy BONK?")
* Token Risk & Security: (e.g., "who are the top holders of pepe?")"""


class Questioner:

    def __init__(
        self,
        api_key: str,
        question_lifetime: timedelta = timedelta(days=7),
        initial_questions: Optional[list[str]] = None,
        question_count: int = 42,
        llm_model: str = "gemini-2.5-flash-lite",
        temperature: float = 1.0,
    ):
        self.question_lifetime = question_lifetime
        self.questions: list[str] = initial_questions or []
        self.last_question_update = datetime.now()

        self.genai_client = genai.Client(api_key=api_key)
        self.llm_model: str = llm_model
        self.question_count: int = question_count
        self.temperature: float = temperature

    def choose_question(self) -> str:
        self.maybe_update_questions()
        return random.choice(self.questions)

    def maybe_update_questions(self):
        if not self.questions or self.is_update_time():
            self.questions = self.generate_exactly_n_questions(n=self.question_count)
            self.last_question_update = datetime.now()

    def is_update_time(self) -> bool:
        return datetime.now() - self.last_question_update > self.question_lifetime

    def generate_exactly_n_questions(self, n: int) -> list[str]:
        new_questions = []
        while len(new_questions) < n:
            qs = self.generate_about_n_questions(n=n - len(new_questions))
            print(f"{len(qs) = }")
            new_questions.extend(qs)
        return new_questions[:n]

    def generate_about_n_questions(self, n: int) -> list[str]:
        class Questions(BaseModel):
            questions: list[str] = Field(..., description="List of crypto questions")

        prompt = GENERATION_PROMPT.format(question_count=n)

        response = self.genai_client.models.generate_content(
            model=self.llm_model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Questions,
                temperature=self.temperature,
            ),
        )

        if response_text := response.text:
            data = json.loads(response_text)
            return data["questions"]
        else:
            bt.logging.warning("No questions were generated!")
            return []
