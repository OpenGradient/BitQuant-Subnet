# The MIT License (MIT)
# Copyright © 2021 Yuma Rao
# Copyright © 2023 Opentensor Foundation
# Copyright © 2023 Opentensor Technologies Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# type: ignore
import bittensor as bt
import random
from typing import List, Optional, Union, Any, Dict
from template.protocol import QuantSynapse, QuantQuery, QuantResponse


class QuantAPI:
    """API for interacting with the Quantitative subnet on Bittensor."""
    
    # Class-level netuid for easy modification
    netuid = 2

    def __init__(self, wallet: "bt.wallet"):
        """
        Initialize the QuantAPI with a wallet.
        
        Args:
            wallet (bt.wallet): The wallet to use for authentication.
        """
        self.wallet = wallet
        self.name = "quant"
        self.subtensor = None
        self.metagraph = None
        self.dendrite = None
        
    def connect(self, subtensor: Optional["bt.subtensor"] = None):
        """
        Connect to the Bittensor network and initialize the metagraph.
        
        Args:
            subtensor (bt.subtensor, optional): The subtensor instance to use.
                If None, a new subtensor instance will be created.
        """
        if subtensor is None:
            self.subtensor = bt.subtensor()
        else:
            self.subtensor = subtensor
            
        # Initialize the metagraph
        self.metagraph = self.subtensor.metagraph(self.netuid)
        
        # Initialize the dendrite
        self.dendrite = bt.dendrite(wallet=self.wallet)
        
        bt.logging.info(f"Connected to Bittensor network with netuid {self.netuid}")
        bt.logging.info(f"Metagraph initialized with {len(self.metagraph.hotkeys)} hotkeys")

    def prepare_synapse(self, query: str, userID: str, metadata: list[str]) -> QuantSynapse:
        """
        Prepare a QuantSynapse object with the given query.
        
        Args:
            query (str): The query string.
            userID (str): The ID of the user making the query.
            metadata (list[str]): Additional metadata for the query.
            
        Returns:
            QuantSynapse: The prepared synapse object.
        """
        # Create a QuantQuery object
        query_obj = QuantQuery(
            query=query,
            userID=userID,
            metadata=metadata
        )
        
        # Create and return a QuantSynapse with the query
        return QuantSynapse(query=query_obj)

    def get_uids(self, k: int = 5, exclude: Optional[List[int]] = None) -> List[int]:
        """
        Get a list of UIDs to query, prioritizing nodes with higher stakes.
        
        Args:
            k (int): The number of UIDs to return.
            exclude (List[int], optional): UIDs to exclude from the result.
            
        Returns:
            List[int]: A list of UIDs to query.
        """
        if self.metagraph is None:
            raise ValueError("Must connect to the network before getting UIDs")
            
        if exclude is None:
            exclude = []
            
        # Get all available UIDs that are not in the exclude list
        available_uids = [uid for uid in range(len(self.metagraph.S)) 
                          if uid not in exclude and self.metagraph.axons[uid] is not None]
        
        # If there are no available UIDs, return an empty list
        if not available_uids:
            return []
            
        # If k is greater than the number of available UIDs, return all available UIDs
        if k >= len(available_uids):
            return available_uids
            
        # Sort UIDs by stake (higher stake first)
        sorted_uids = sorted(available_uids, key=lambda uid: float(self.metagraph.S[uid]), reverse=True)
        
        # Return the top k UIDs
        return sorted_uids[:k]

    def query(self, uids, query: str, userID: str, metadata: list[str], timeout: float = 12.0):
        """
        Query the network with the given parameters.
        
        Args:
            uids (List[int]): The UIDs to query.
            query (str): The query string.
            userID (str): The ID of the user making the query.
            metadata (list[str]): Additional metadata for the query.
            timeout (float, optional): The query timeout in seconds.
            
        Returns:
            List[QuantSynapse]: The responses from the network.
        """
        if self.metagraph is None or self.dendrite is None:
            raise ValueError("Must connect to the network before querying")
            
        # Prepare the synapse with the query
        synapse = self.prepare_synapse(query, userID, metadata)
        
        # Get the axons to query
        axons = [self.metagraph.axons[uid] for uid in uids if self.metagraph.axons[uid] is not None]
        
        if not axons:
            bt.logging.warning("No valid axons to query")
            return []
            
        # Query the network
        bt.logging.info(f"Querying {len(axons)} axons with timeout {timeout}s")
        responses = self.dendrite.query(
            axons=axons,
            synapse=synapse,
            deserialize=True,
            timeout=timeout
        )
        
        return responses

    def process_responses(self, responses: List[Union["bt.Synapse", Any]]):
        """
        Process the responses from the network.
        
        Args:
            responses (List[Union[bt.Synapse, Any]]): The responses from the network.
            
        Returns:
            List[QuantResponse]: The processed responses.
        """
        outputs = []
        for response in responses:
            # Skip responses with non-200 status codes
            if hasattr(response, 'dendrite') and response.dendrite.status_code != 200:
                continue
                
            # Add the response to the outputs
            if hasattr(response, 'response') and response.response is not None:
                outputs.append(response.response)
                
        return outputs
