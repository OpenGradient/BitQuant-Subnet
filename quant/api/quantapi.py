# The MIT License (MIT)
# Copyright © 2025 Quant by OpenGradient

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
import sys
import traceback
from typing import List, Optional, Union, Any, Dict
from quant.protocol import QuantSynapse, QuantQuery, QuantResponse


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
        print(f"Initializing QuantAPI with wallet {wallet}")
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
        try:
            if subtensor is None:
                print("No subtensor provided, creating a new one...")
                self.subtensor = bt.subtensor()
            else:
                print("Using provided subtensor instance")
                self.subtensor = subtensor
                
            # Check if subtensor is connected
            try:
                block = self.subtensor.get_current_block()
                print(f"Subtensor connected successfully. Current block: {block}")
            except Exception as e:
                print(f"Error checking subtensor connection: {e}")
                raise
                
            # Initialize the metagraph
            print(f"Initializing metagraph for netuid {self.netuid}")
            self.metagraph = self.subtensor.metagraph(self.netuid)
            
            # Do a sanity check on the metagraph
            if self.metagraph is None:
                raise ValueError("Failed to initialize metagraph")
                
            print(f"Metagraph initialized with {len(self.metagraph.hotkeys)} hotkeys")
            
            # Initialize the dendrite with wallet
            print(f"Initializing dendrite with wallet {self.wallet}")
            self.dendrite = bt.dendrite(wallet=self.wallet)
            
            # Count active axons
            active_axons = sum(1 for axon in self.metagraph.axons if axon is not None and self._is_axon_valid(axon))
            
            print(f"Connected to Bittensor network with netuid {self.netuid}")
            print(f"Metagraph has {active_axons} active axons out of {len(self.metagraph.axons)} total")
            
            return True
            
        except Exception as e:
            print(f"Error connecting to Bittensor network: {e}")
            traceback.print_exc()
            return False
    
    def _is_axon_valid(self, axon):
        """Check if an axon has valid connection details."""
        if axon is None:
            return False
            
        # Check for valid IP and port
        return (
            hasattr(axon, 'ip') and 
            axon.ip is not None and 
            len(axon.ip) > 0 and
            hasattr(axon, 'port') and 
            axon.port is not None and 
            axon.port > 0
        )

    def prepare_synapse(self, query: str, userID: str, metadata: dict) -> QuantSynapse:
        """
        Prepare a QuantSynapse with the given query and userID.
        
        Args:
            query (str): The query string.
            userID (str): The user ID for the query.
            metadata (dict): Any additional metadata to include with the query.
            
        Returns:
            QuantSynapse: The prepared synapse.
        """
        # Create a QuantQuery
        quant_query = QuantQuery(
            query=query,
            userID=userID,
            metadata=metadata
        )
        
        # Create and return a QuantSynapse with the query
        return QuantSynapse(query=quant_query)

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
            print("WARNING: Metagraph is None when getting UIDs")
            return []
            
        if exclude is None:
            exclude = []
            
        # Get all available UIDs with valid axons
        available_uids = []
        for uid in range(len(self.metagraph.axons)):
            if uid in exclude:
                continue
                
            axon = self.metagraph.axons[uid]
            if axon is not None and self._is_axon_valid(axon):
                available_uids.append(uid)
                
        print(f"Found {len(available_uids)} available UIDs with valid axons")
        
        # If there are no available UIDs, return an empty list
        if not available_uids:
            print("WARNING: No available UIDs with valid axons found")
            return []
            
        # If k is greater than the number of available UIDs, return all available UIDs
        if k >= len(available_uids):
            return available_uids
            
        # Sort UIDs by stake (higher stake first)
        sorted_uids = sorted(available_uids, key=lambda uid: float(self.metagraph.S[uid]), reverse=True)
        
        # Return the top k UIDs
        return sorted_uids[:k]

    def query(self, uids, query: str, userID: str, metadata: dict, timeout: float = 12.0):
        """
        Query the network with the given query.
        
        Args:
            uids: The UIDs to query.
            query (str): The query string.
            userID (str): The user ID for the query.
            metadata (dict): Any additional metadata to include with the query.
            timeout (float): The timeout for the query in seconds.
            
        Returns:
            List[QuantResponse]: The responses from the network.
        """
        if self.metagraph is None or self.dendrite is None:
            print("WARNING: Metagraph or dendrite is None when querying")
            return []
            
        try:
            # Prepare the synapse with the query
            synapse = self.prepare_synapse(query, userID, metadata)
            
            # Get the axons to query (only those with valid connection details)
            valid_axons = []
            for uid in uids:
                if uid >= len(self.metagraph.axons):
                    print(f"WARNING: UID {uid} is out of range")
                    continue
                    
                axon = self.metagraph.axons[uid]
                if axon is not None and self._is_axon_valid(axon):
                    valid_axons.append(axon)
                else:
                    print(f"WARNING: Skipping UID {uid} due to invalid axon")
            
            if not valid_axons:
                print("WARNING: No valid axons to query")
                return []
                
            # Query the network
            print(f"Querying {len(valid_axons)} axons with timeout {timeout}s")
            for i, axon in enumerate(valid_axons):
                print(f"  Axon {i+1}: {axon.ip}:{axon.port} (UID: {uids[i] if i < len(uids) else 'unknown'})")
                
            responses = self.dendrite.query(
                axons=valid_axons,
                synapse=synapse,
                deserialize=True,
                timeout=timeout
            )
            
            print(f"Received {len(responses)} responses")
            return responses
            
        except Exception as e:
            print(f"Error querying the network: {e}")
            traceback.print_exc()
            return []

    def process_responses(self, responses: List[Union["bt.Synapse", Any]]):
        """
        Process the responses from the network.
        
        Args:
            responses (List[Union[bt.Synapse, Any]]): The responses from the network.
            
        Returns:
            List[QuantResponse]: The processed responses.
        """
        outputs = []
        
        if not responses:
            print("WARNING: No responses to process")
            return outputs
            
        try:
            for i, response in enumerate(responses):
                print(f"Processing response {i+1}")
                
                # Check if the response is already a QuantResponse object
                if isinstance(response, QuantResponse):
                    print(f"  Response {i+1} is already a QuantResponse")
                    outputs.append(response)
                    continue
                
                # For traditional format responses with dendrite attribute
                if hasattr(response, 'dendrite'):
                    # Skip responses with non-200 status codes
                    if response.dendrite.status_code != 200:
                        print(f"  Skipping response {i+1} with status code {response.dendrite.status_code}")
                        continue
                        
                    # Check if response has a valid response attribute
                    if not hasattr(response, 'response') or response.response is None:
                        print(f"  WARNING: Response {i+1} has no 'response' attribute or it's None")
                        continue
                    
                    # Check if the response attribute is already a QuantResponse
                    if isinstance(response.response, QuantResponse):
                        print(f"  Response {i+1}.response is a QuantResponse, adding to outputs")
                        outputs.append(response.response)
                    else:
                        print(f"  WARNING: Response {i+1}.response is not a QuantResponse")
                        # Try to handle the case where response.response is the actual content
                        try:
                            # If it's a dictionary, try to create a QuantResponse from it
                            if isinstance(response.response, dict) and 'response' in response.response:
                                print(f"  Attempting to create QuantResponse from dictionary")
                                quant_response = QuantResponse(
                                    response=response.response.get('response'),
                                    signature=response.response.get('signature'),
                                    proofs=response.response.get('proofs'),
                                    metadata=response.response.get('metadata', {})
                                )
                                outputs.append(quant_response)
                            else:
                                print(f"  Could not process response {i+1} with type {type(response.response)}")
                        except Exception as e:
                            print(f"  Error creating QuantResponse from dictionary: {e}")
                else:
                    # Handle responses without dendrite attribute but with a response attribute
                    if hasattr(response, 'response'):
                        print(f"  Response {i+1} has no 'dendrite' attribute but has 'response'")
                        
                        if isinstance(response.response, QuantResponse):
                            print(f"  Response {i+1}.response is a QuantResponse, adding to outputs")
                            outputs.append(response.response)
                        else:
                            print(f"  Response {i+1}.response is not a QuantResponse, skipping")
                    else:
                        print(f"  WARNING: Response {i+1} has no 'dendrite' attribute and no 'response' attribute")
                
            print(f"Processed {len(outputs)} valid responses out of {len(responses)} total")
            return outputs
                
        except Exception as e:
            print(f"Error processing responses: {e}")
            traceback.print_exc()
            return []
