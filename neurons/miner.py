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

import time
import typing
import bittensor as bt

# Bittensor Miner Quant:
import quant

# Import the subnet_query function from TwoLigma client
from quant.TwoLigma.api.simple_client import subnet_query

# import base miner class which takes care of most of the boilerplate
from quant.base.miner import BaseMinerNeuron

# Import the shared Quant agent server module
from neurons import quant_agent_server

class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)

        # Disable validator requirement for testing
        self.config.blacklist.force_validator_permit = False

        # TODO(developer): Anything specific to your use case you can do here

    async def forward(
        self, synapse: quant.protocol.QuantSynapse
    ) -> quant.protocol.QuantSynapse:
        """
        Processes the incoming 'QuantSynapse' request by forwarding it to the TwoLigma subnet
        using the subnet_query function.

        Args:
            synapse (quant.protocol.QuantSynapse): The synapse object containing the query.

        Returns:
            quant.protocol.QuantSynapse: The synapse object with the response set.
        """
        try:
            # Check if query is properly set
            if not hasattr(synapse, 'query') or synapse.query is None:
                bt.logging.warning("Received synapse with no query")
                # Create a proper QuantResponse object
                response = quant.protocol.QuantResponse(
                    response="Error: No query provided",
                    signature=b"error",
                    proofs=[b"error"],
                    metadata={}
                )
                # Convert to dictionary and set response
                synapse.response = response.dict()
            else:
                bt.logging.info(f"Processing query: {synapse.query.query}")
                bt.logging.info(f"From userID: {synapse.query.userID}")
                bt.logging.info(f"Metadata: {synapse.query.metadata}")
                
                # Forward the query to the quant agent using subnet_query
                response = subnet_query(synapse.query)
                
                if response is None:
                    # Create a fallback response 
                    bt.logging.warning("Failed to get response from agent. Creating fallback response.")
                    response = quant.protocol.QuantResponse(
                        response="The server could not process your request at this time. Please try again later.",
                        signature=b"error",
                        proofs=[b"error"],
                        metadata=synapse.query.metadata or {}
                    )
                    # Convert to dictionary and set response
                    synapse.response = response.dict()
                else:
                    bt.logging.info(f"Received response from quant agent: {response.response[:100]}...")
                    # Convert QuantResponse to dictionary
                    synapse.response = response.dict()
                    
            return synapse
        except Exception as e:
            bt.logging.error(f"Error in forward: {e}")
            # Create error response as dictionary
            synapse.response = quant.protocol.QuantResponse(
                response=f"Error processing request: {str(e)}",
                signature=b"error",
                proofs=[b"error"],
                metadata={}
            ).dict()
            return synapse

    async def blacklist(
        self, synapse: quant.protocol.QuantSynapse
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored.
        """
        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return True, "Missing dendrite or hotkey"

        # TODO(developer): Define how miners should blacklist requests.
        uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
        if (
            not self.config.blacklist.allow_non_registered
            and synapse.dendrite.hotkey not in self.metagraph.hotkeys
        ):
            # Ignore requests from un-registered entities.
            bt.logging.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        if self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                bt.logging.warning(
                    f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
                )
                return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(
        self, synapse: quant.protocol.QuantSynapse
    ) -> float:
        """
        The priority function determines the order in which requests are handled.
        """
        # Get the dendrite.hotkey from axon_info if it exists
        hotkey = None
        if hasattr(synapse, 'dendrite') and synapse.dendrite is not None:
            hotkey = synapse.dendrite.hotkey
        elif hasattr(synapse, 'axon_info') and synapse.axon_info is not None:
            hotkey = synapse.axon_info.hotkey
            
        if hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return 0.0

        # TODO(developer): Define how miners should prioritize requests.
        try:
            caller_uid = self.metagraph.hotkeys.index(hotkey)
            priority = float(self.metagraph.S[caller_uid])  # Return the stake as the priority.
        except (ValueError, KeyError, IndexError) as e:
            # If the hotkey is not in the metagraph or any other indexing error, return 0 priority
            bt.logging.trace(f"Error getting priority for {hotkey}: {e}")
            priority = 0.0
            
        bt.logging.trace(
            f"Prioritizing {hotkey} with value: {priority}"
        )
        return priority

# This is the main function, which runs the miner.
if __name__ == "__main__":
    try:
        # Set up and start the Quant agent server using the shared module
        quant_agent_server_process = quant_agent_server.setup_quant_agent_server()
        
        # Log whether we're using an existing server or started a new one
        if quant_agent_server_process is None:
            bt.logging.info("Using an existing Quant agent server or continuing without one.")
        else:
            bt.logging.info(f"Started a new Quant agent server with PID: {quant_agent_server_process.pid}")
            
        with Miner() as miner:
            bt.logging.info("Starting miner...")
            while True:
                bt.logging.info(f"Miner running... {time.time()}")
                
                # Check if Quant agent server is still running (only if we're managing it)
                if quant_agent_server_process is not None and not quant_agent_server.check_quant_agent_server(quant_agent_server_process):
                    bt.logging.error("Quant agent server is no longer running.")
                    bt.logging.warning("Continuing miner operation, but queries may fail.")
                    # Set to None so we don't keep checking
                    quant_agent_server_process = None
                
                time.sleep(5)
    except KeyboardInterrupt:
        bt.logging.info("Keyboard interrupt received. Exiting miner.")
    except Exception as e:
        bt.logging.error(f"Error running miner: {e}")
        import traceback
        bt.logging.debug(f"Stack trace: {traceback.format_exc()}")
        raise
    finally:
        # The cleanup will be handled by the atexit handler in the shared module.
        # Since we registered the atexit handler in quant_agent_server, it will only clean up
        # the server if it was started by this process.
        pass
