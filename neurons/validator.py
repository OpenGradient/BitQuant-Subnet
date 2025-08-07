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
import sys

# Bittensor
import bittensor as bt

# import base validator class which takes care of most of the boilerplate
from quant.base.validator import BaseValidatorNeuron

# Bittensor Validator Quant:
from quant.validator import forward

# Import the shared Quant agent server module
from neurons import quant_agent_server

class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()

        # TODO(developer): Anything specific to your use case you can do here

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        # TODO(developer): Rewrite this function based on your protocol definition.
        return await forward(self)

# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    try:
        # Set up and start the Quant agent server using the shared module
        # quant_agent_server_process = quant_agent_server.setup_quant_agent_server()
        quant_agent_server_process = None 

        # Log whether we're using an existing server or started a new one
        if quant_agent_server_process is None:
            bt.logging.info("Using an existing Quant agent server or continuing without one.")
        else:
            bt.logging.info(f"Started a new Quant agent server with PID: {quant_agent_server_process.pid}")
            
        with Validator() as validator:
            while True:
                bt.logging.info(f"Validator running... {time.time()}")
                
                # Check if Quant agent server is still running (only if we're managing it)
                if quant_agent_server_process is not None and not quant_agent_server.check_quant_agent_server(quant_agent_server_process):
                    bt.logging.error("Quant agent server is no longer running.")
                    bt.logging.warning("Continuing validator operation, but queries may fail.")
                    # Set to None so we don't keep checking
                    quant_agent_server_process = None
                    
                time.sleep(5)
    except KeyboardInterrupt:
        bt.logging.info("Keyboard interrupt received. Exiting validator.")
    except Exception as e:
        bt.logging.error(f"Error running validator: {e}")
        import traceback
        bt.logging.debug(f"Stack trace: {traceback.format_exc()}")
        raise
    finally:
        # The cleanup will be handled by the atexit handler in the shared module.
        # Since we registered the atexit handler in quant_agent_server, it will only clean up
        # the server if it was started by this process.
        pass
