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
from typing import List, Optional, Dict, Any
import bittensor as bt
from quant.protocol import QuantResponse, QuantQuery
# from quant.BitQuant.subnet.subnet_methods import subnet_evaluation
from quant.validator.attestation.attestation import retrieve_remote_attestation, validate_attestation
from quant.validator.attestation.periodic import periodic_attestation_check

# Start periodic attestation check
periodic_attestation_check()


def bitquant_evaluate(
    query: QuantQuery, 
    response: QuantResponse, 
    api_url: str = "https://quant-api.opengradient.ai/api/subnet/evaluate",
    timeout: float = 60.0
) -> Optional[Dict[str, Any]]:
    """
    Helper function to evaluate a miner's response using the BitQuant Agent API.
    The current implementation uses the production BitQuant Agent deployment 
    (see https://github.com/OpenGradient/BitQuant), but we welcome validators to design 
    their own subnet query evaluation mechanism.
    
    Args:
        query (QuantQuery): The query that was sent to the miner
        response (QuantResponse): The response received from the miner  
        api_url (str): The BitQuant Agent API endpoint URL
        timeout (float): Request timeout in seconds
        
    Returns:
        Optional[Dict[str, Any]]: The evaluation result from the API, or None if failed
    """
    try:
        # Prepare the payload matching the expected API format
        payload = {
            "quant_query": {
                "query": query.query,
                "userID": query.userID,
                "metadata": query.metadata
            },
            "quant_response": {
                "response": response.response,
                "signature": response.signature.hex() if isinstance(response.signature, bytes) else str(response.signature),
                "proofs": [proof.hex() if isinstance(proof, bytes) else str(proof) for proof in response.proofs],
                "metadata": response.metadata
            }
        }
        
        # Make the API request
        headers = {
            'Content-Type': 'application/json'
        }
        
        bt.logging.debug(f"Making evaluation request to {api_url}")
        bt.logging.trace(f"Payload: {json.dumps(payload, indent=2)}")
        
        response_obj = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        # Check if request was successful
        response_obj.raise_for_status()
        
        # Parse JSON response
        evaluation_result = response_obj.json()
        
        bt.logging.debug(f"Received evaluation result: {evaluation_result}")
        return evaluation_result
        
    except requests.exceptions.Timeout:
        bt.logging.warning(f"Timeout occurred while calling BitQuant Agent API (timeout: {timeout}s)")
        return None
    except requests.exceptions.ConnectionError:
        bt.logging.warning("Connection error occurred while calling BitQuant Agent API")
        return None
    except requests.exceptions.HTTPError as e:
        bt.logging.warning(f"HTTP error occurred while calling BitQuant Agent API: {e}")
        return None
    except json.JSONDecodeError:
        bt.logging.warning("Failed to decode JSON response from BitQuant Agent API")
        return None
    except Exception as e:
        bt.logging.error(f"Unexpected error occurred while calling BitQuant Agent API: {e}")
        return None


def subnet_evaluation(query: QuantQuery, response: QuantResponse) -> float:
    """
    Evaluate a miner's response using the BitQuant Agent API and return a reward score.
    
    Args:
        query (QuantQuery): The query that was sent to the miner
        response (QuantResponse): The response received from the miner
        
    Returns:
        float: Reward score between 0.0 and 1.0
    """
    try:
        # Call the BitQuant Agent API for evaluation
        evaluation_result = bitquant_evaluate(query, response)
        
        if evaluation_result is None:
            bt.logging.warning("Failed to get evaluation from BitQuant Agent API, returning default score")
            return 0.0
            
        # Extract score from the evaluation result
        # The API response format may vary, so we handle different possible structures
        score = 0.0
        
        if isinstance(evaluation_result, dict):
            # Try different possible score field names
            if 'score' in evaluation_result:
                score = float(evaluation_result['score'])
            elif 'reward' in evaluation_result:
                score = float(evaluation_result['reward'])
            elif 'evaluation_score' in evaluation_result:
                score = float(evaluation_result['evaluation_score'])
            elif 'rating' in evaluation_result:
                score = float(evaluation_result['rating'])
            else:
                bt.logging.warning(f"Unexpected evaluation result format: {evaluation_result}")
                return 0.0
                
        # Ensure score is within valid range [0.0, 1.0]
        score = max(0.0, min(1.0, score))
        
        bt.logging.info(f"BitQuant Agent API evaluation score: {score}")
        return score
        
    except (ValueError, TypeError) as e:
        bt.logging.error(f"Error parsing evaluation score: {e}")
        return 0.0
    except Exception as e:
        bt.logging.error(f"Unexpected error in subnet_evaluation: {e}")
        return 0.0

def reward(query: QuantQuery, response: QuantResponse) -> float:
    """
    Calculate the reward for a miner's response to a given query.
    Uses the subnet_evaluation function to determine the quality of the response.

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
