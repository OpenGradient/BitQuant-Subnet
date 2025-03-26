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
from template.protocol import QuantResponse, QuantQuery

def reward(query: QuantQuery, response: QuantResponse) -> float:
    """
    Calculate the reward for a miner's response to a given query. This function evaluates the response
    and returns a reward value that is used to update the miner's score.

    Args:
    - query (QuantQuery): The query sent to the miner.
    - response (QuantResponse): The response received from the miner.

    Returns:
    - float: The reward value for the miner.
    """
    bt.logging.info(
        f"Rewarding test amount 0.69"
    )
    return 0.69 


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
    # Get all the reward results by iteratively calling your reward() function.

    return np.array([reward(query, response) for response in responses])
