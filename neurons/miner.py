# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

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

# Bittensor Miner Template:
import template

# import base miner class which takes care of most of the boilerplate
from template.base.miner import BaseMinerNeuron

class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)

        # TODO(developer): Anything specific to your use case you can do here

    async def forward(
        self, synapse: template.protocol.QuantSynapse
    ) -> template.protocol.QuantSynapse:
        """
        Processes the incoming 'QuantSynapse' request by generating an appropriate response.

        Args:
            synapse (template.protocol.QuantSynapse): The synapse object containing the query.

        Returns:
            template.protocol.QuantSynapse: The synapse object with the response set.
        """
        try:
            # Check if query is properly set
            if not hasattr(synapse, 'query') or synapse.query is None:
                bt.logging.warning("Received synapse with no query")
                response = template.protocol.QuantResponse(
                    response="Error: No query provided",
                    signature=b"error",
                    proofs=[b"error"],
                    metadata=[]
                )
            else:
                # TODO(developer): Replace with actual implementation logic.
                response = template.protocol.QuantResponse(
                    response=f"Response to: {synapse.query.query}",
                    signature=b"dummy_signature",
                    proofs=[b"dummy_proof"],
                    metadata=synapse.query.metadata or []
                )
                
            synapse.set_response(response)
            return synapse
        except Exception as e:
            bt.logging.error(f"Error in forward: {e}")
            # Provide a fallback response in case of error
            error_response = template.protocol.QuantResponse(
                response=f"Error processing request: {str(e)}",
                signature=b"error",
                proofs=[b"error"],
                metadata=[]
            )
            synapse.set_response(error_response)
            return synapse

    async def blacklist(
        self, synapse: template.protocol.QuantSynapse
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored.
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
            return True, "Missing dendrite or hotkey"

        # TODO(developer): Define how miners should blacklist requests.
        try:
            uid = self.metagraph.hotkeys.index(hotkey)
        except ValueError:
            # Hotkey not found in metagraph
            if not self.config.blacklist.allow_non_registered:
                bt.logging.trace(
                    f"Blacklisting un-registered hotkey {hotkey}"
                )
                return True, "Unrecognized hotkey"
            uid = -1  # Invalid UID for hotkeys not in metagraph

        if uid != -1 and self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                bt.logging.warning(
                    f"Blacklisting a request from non-validator hotkey {hotkey}"
                )
                return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(
        self, synapse: template.protocol.QuantSynapse
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
        with Miner() as miner:
            bt.logging.info("Starting miner...")
            while True:
                bt.logging.info(f"Miner running... {time.time()}")
                time.sleep(5)
    except KeyboardInterrupt:
        bt.logging.info("Keyboard interrupt received. Exiting miner.")
    except Exception as e:
        bt.logging.error(f"Error running miner: {e}")
        import traceback
        bt.logging.debug(f"Stack trace: {traceback.format_exc()}")
        raise
