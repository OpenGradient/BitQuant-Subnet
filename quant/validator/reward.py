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
import opengradient as og
from opengradient import LlmInferenceMode

# from quant.BitQuant.subnet.subnet_methods import subnet_evaluation
from quant.validator.attestation.attestation import retrieve_remote_attestation, validate_attestation
from quant.validator.attestation.periodic import periodic_attestation_check

# Start periodic attestation check
periodic_attestation_check()


# Model Configuration
# Validators specify which model they want to use for evaluation
# Examples:
#   - "gemini-2.5-flash-lite" (Google)
#   - "claude-haiku-4-5-20251001" (Anthropic)
#   - "gpt-4o-mini" (OpenAI)
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")

# Provider API Keys
# Validators must provide the API key corresponding to their chosen model
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenGradient Network Configuration
OPENGRADIENT_PRIVATE_KEY = os.getenv("OPENGRADIENT_PRIVATE_KEY") 
OPENGRADIENT_RPC_URL = os.getenv("OPENGRADIENT_RPC_URL", "http://18.218.115.248:8545")

OPENGRADIENT_CONTRACT_ADDRESS = os.getenv("OPENGRADIENT_CONTRACT_ADDRESS", "0xF78F7d5a7e9f484f0924Cc21347029715bD3B8f4")
# tocheck with kyle
# Security check API
SECURITY_CHECK_URL = "https://quant-api.opengradient.ai/api/subnet/security-check"

# Template setup
TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

# Global OpenGradient client
_og_client = None


def get_og_client() -> og.Client:
    """
    Initialize and return the OpenGradient SDK client.
    
    
    Returns:
        og.Client: Initialized OpenGradient client instance
        
    Raises:
        ValueError: If no API keys are configured
    """
    global _og_client
    
    if _og_client is None:
        try:
            # Build client configuration with all network parameters
            client_config = {
                "api_url": "https://api.opengradient.ai/v1", 
                "rpc_url": OPENGRADIENT_RPC_URL,
                "contract_address": OPENGRADIENT_CONTRACT_ADDRESS,
            }
            
            # Private key is REQUIRED by SDK
            if OPENGRADIENT_PRIVATE_KEY:
                # Use provided key
                client_config["private_key"] = OPENGRADIENT_PRIVATE_KEY
            else:
                test_key = "5ad9b639f7172b5b99936b1dfa1f95c04c4a9d2f4ea26019b2f3a65c4ecb3e59"
                client_config["private_key"] = test_key
                bt.logging.warning("⚠️  Using test private key (development only, not for production)")
            
            # Add all available API keys - SDK will use the correct one based on model
            api_keys_added = []
            if GOOGLE_API_KEY:
                client_config["google_api_key"] = GOOGLE_API_KEY
                api_keys_added.append("Google")
            if ANTHROPIC_API_KEY:
                client_config["anthropic_api_key"] = ANTHROPIC_API_KEY
                api_keys_added.append("Anthropic")
            if OPENAI_API_KEY:
                client_config["openai_api_key"] = OPENAI_API_KEY
                api_keys_added.append("OpenAI")
            
            # Verify at least one API key is configured
            if not api_keys_added:
                raise ValueError(
                    "No API keys configured. Please set at least one of: "
                    "GOOGLE_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY"
                )
            
            # Initialize OpenGradient client
            _og_client = og.Client(**client_config)
            
            bt.logging.info(
                f"✅ OpenGradient SDK client initialized\n"
                f"   Model: {LLM_MODEL}\n"
                f"   Available providers: {', '.join(api_keys_added)}\n"
                f"   Network: {OPENGRADIENT_RPC_URL}"
            )
            
        except Exception as e:
            bt.logging.error(f"❌ Failed to initialize OpenGradient client: {e}")
            raise
    
    return _og_client


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
    Call LLM for evaluation via OpenGradient Network.

    
    Args:
        prompt (str): The evaluation prompt
        
    Returns:
        float: Normalized score between 0.0 and 1.0
    """
    try:
        client = get_og_client()
        
        bt.logging.info(f"🔄 Routing evaluation request through OpenGradient Network...")
        bt.logging.debug(f"   Model: {LLM_MODEL}")
        

        result = client.llm_completion(
            model_cid=LLM_MODEL,
            inference_mode=LlmInferenceMode.VANILLA,
            prompt=prompt,
            max_tokens=200
        )
        
        # Extract completion output
        response_text = result.completion_output
        
        if not response_text:
            raise ValueError("Empty response from OpenGradient SDK")
        
        bt.logging.debug(f"Raw response: {response_text[:200]}")
        
        # Clean response (remove markdown formatting if present)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Parse JSON response
        try:
            data = json.loads(response_text)
            score = float(data["score"])
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            bt.logging.error(f"❌ Invalid JSON response: {response_text}")
            raise ValueError(f"Failed to parse score from response: {e}")
        
        # Validate and clamp score to expected range [0, 50]
        if not (0 <= score <= 50):
            bt.logging.warning(f"⚠️ Score {score} outside [0, 50], clamping...")
            score = max(0, min(50, score))
        
        # Normalize to [0, 1]
        normalized_score = score / 50.0
        
        bt.logging.info(f"✅ Evaluation complete: {score}/50 → {normalized_score:.3f}")
        
        return normalized_score
        
    except Exception as e:
        bt.logging.error(f"❌ LLM evaluation failed: {e}")
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