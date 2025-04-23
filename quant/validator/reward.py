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
from typing import List
import bittensor as bt
from quant.protocol import QuantResponse, QuantQuery
from quant.BitQuant.subnet.subnet_methods import subnet_evaluation
from quant.validator.attestation.attestation import retrieve_remote_attestation, validate_attestation
from quant.validator.attestation.periodic import periodic_attestation_check

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
    try:
        attestation = retrieve_remote_attestation()
        if not validate_attestation(attestation):
            bt.logging.warning("TEE GPU attestation failed. Reward set to 0.")
            return 0.0
    except Exception as e:
        bt.logging.error(f"TEE attestation error: {e}. Reward set to 0.")
        return 0.0

    bt.logging.info(f"Evaluating response for query: {query} and response: {response}")
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


def periodic_attestation_check(interval_seconds: int = 3600):
    """
    Runs attestation validation at the top of every hour (default) in a background thread.
    """
    def _job():
        while True:
            now = time.time()
            # Calculate seconds until the next hour
            seconds_until_next_hour = 3600 - (int(now) % 3600)
            bt.logging.info(f"Sleeping {seconds_until_next_hour}s until next attestation check...")
            time.sleep(seconds_until_next_hour)
            try:
                nonce = generate_nonce()
                bt.logging.info(f"Running attestation check at epoch hour nonce: {nonce}")
                attestation = retrieve_remote_attestation(nonce)
                if validate_attestation(attestation):
                    bt.logging.info("[Attestation] SUCCESS")
                else:
                    bt.logging.warning("[Attestation] FAILURE")
            except Exception as e:
                bt.logging.error(f"[Attestation] ERROR: {e}")
    thread = threading.Thread(target=_job, daemon=True)
    thread.start()

if __name__ == "__main__":
    bt.logging.info("Starting periodic attestation check (every hour)...")
    periodic_attestation_check()
    # Keep the main thread alive
    while True:
        time.sleep(60)
