# The MIT License (MIT)
# Copyright © 2025 Quant by OpenGradient

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
import numpy as np
import requests
import json
import os
from typing import List, Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader
import pathlib
import bittensor as bt
from quant.protocol import QuantResponse, QuantQuery
# from quant.BitQuant.subnet.subnet_methods import subnet_evaluation
from quant.validator.attestation.attestation import retrieve_remote_attestation, validate_attestation
from quant.validator.attestation.periodic import periodic_attestation_check

# Start periodic attestation check
periodic_attestation_check()

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")

# Security check API
SECURITY_CHECK_URL = "https://quant-api.opengradient.ai/api/subnet/security-check"

# Template setup
TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def check_security(query: QuantQuery, response: QuantResponse) -> bool:
    """Check security with your server API"""
    try:
        payload = {
            "quant_query": {"query": query.query, "userID": query.userID, "metadata": query.metadata},
            "quant_response": {
                "response": response.response,
                "signature": response.signature.hex() if isinstance(response.signature, bytes) else str(response.signature),
                "proofs": [proof.hex() if isinstance(proof, bytes) else str(proof) for proof in response.proofs],
                "metadata": response.metadata
            }
        }
        result = requests.post(SECURITY_CHECK_URL, json=payload, timeout=10.0)
        return result.json().get("passed", False)
    except Exception as e:
        bt.logging.error(f"Security check failed: {e}")
        return False


def call_llm(prompt: str) -> float:
    """
    Call the evaluation model (Gemini) with the given prompt and return a normalized score (0–1).

    This function currently supports only the Gemini model. 
    You may extend it to integrate additional LLM providers if needed.

    Args:
        prompt (str): The evaluation prompt to send to the model.

    Returns:
        float: Normalized score between 0 and 1.

    Raises:
        ValueError: If the provider is unsupported or response is invalid.
    """
    if LLM_PROVIDER.lower() != "gemini":
        raise ValueError(
            f"Unsupported LLM_PROVIDER: '{LLM_PROVIDER}'. "
            "Currently only 'gemini' is supported. "
            "You may update this function to integrate your preferred LLM API."
        )

    try:
        import google.genai as genai
        from google.genai import types
        from pydantic import BaseModel, Field

        # Configure Gemini client
        genai.configure(api_key=LLM_API_KEY)
        client = genai.Client()

        # Define structured response schema
        class Scoring(BaseModel):
            score: int = Field(..., description="The final score of the response")

        # Generate structured content from Gemini
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Scoring,
                max_output_tokens=200,
                temperature=0.0,
            ),
        )

        # Parse model response
        try:
            data = json.loads(response.text)
            score = float(data["score"])
        except Exception:
            bt.logging.error(f"Invalid Gemini response: {response.text}")
            raise ValueError(
                "Gemini response did not contain valid JSON with a 'score' field. "
                "Ensure your evaluation prompt enforces structured JSON output."
            )

        # Normalize to 0–1 range (assuming original scale 0–50)
        return score / 50.0

    except Exception as e:
        bt.logging.error(f"Failed to call Gemini evaluation model: {e}")
        raise

def subnet_evaluation(query: QuantQuery, response: QuantResponse) -> float:
    """Evaluate with security check + local LLM"""
    try:
        # Security check 
        if not check_security(query, response):
            bt.logging.warning("Security check failed")
            return 0.0
        
        # Load prompt template
        template = env.get_template("evaluation_prompt.txt")
        prompt = template.render(user_prompt=query.query, agent_answer=response.response[:4000])
        
        # Call validator's LLM
        score = call_llm(prompt)
        score = max(0.0, min(1.0, score))
        
        bt.logging.info(f"Evaluation score: {score}")
        return score
        
    except Exception as e:
        bt.logging.error(f"Evaluation error: {e}")
        return 0.0


def reward(query: QuantQuery, response: QuantResponse) -> float:
    """
    Calculate the reward for a miner's response to a given query.
    Uses local evaluation instead of calling external API.

    Args:
    - query (QuantQuery): The query sent to the miner.
    - response (QuantResponse): The response received from the miner.

    Returns:
    - float: The reward value for the miner.
    """

    """
    TEE remote attestation check -> no hard TEE attestation check requirement for now
    try:
        attestation = retrieve_remote_attestation()
        if not validate_attestation(attestation):
            bt.logging.warning("TEE GPU attestation failed. Reward set to 0.")
            return 0.0
    except Exception as e:
        bt.logging.error(f"TEE attestation error: {e}. Reward set to 0.")
        return 0.0
    """
    bt.logging.info(f"Evaluating response for query: {query} and response: {response}")
  # Validate the response before evaluation
    if response is None:
        bt.logging.warning("Response is None, returning reward score of 0.0")
        return 0.0
    
    # Check if response has valid response content
    if not hasattr(response, 'response') or not response.response:
        bt.logging.warning("Response does not contain valid response content, returning reward score of 0.0")
        return 0.0

    # TODO(developer): Developers can deploy their own evaluation function here.
    # Replace 'subnet_evaluation' with your custom evaluation logic as needed.
    # Perform local evaluation
    reward_score = subnet_evaluation(query, response)
    return reward_score


def get_rewards(
    self,
    query: QuantQuery,
    responses: List[QuantResponse],
) -> np.ndarray:
    """
    Calculate and return an array of rewards for the provided query and corresponding responses.

    Args:
    - query (QuantQuery): The query sent to the miner.
    - responses (List[QuantResponse]): A list of QuantResponse objects received from the miner.

    Returns:
    - np.ndarray: An array of reward values for each response based on the given query.
    """
    return np.array([reward(query, response) for response in responses])