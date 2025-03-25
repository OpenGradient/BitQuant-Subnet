# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

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

import typing
import bittensor as bt

# TODO(developer): Clean up comments

class QuantQuery:
    def __init__(self, query: str, userID: str, metadata: list[str]):
        """
        Initializes a QuantQuery object.

        Args:
            query (str): The query string to be sent to the miner.
            userID (str): The wallet address of the user the query is designed for.
            metadata (list[str]): Additional metadata related to the query.
        """
        self.query = query
        self.userID = userID
        self.metadata = metadata

class QuantResponse:
    def __init__(self, response: str, signature: bytes, proofs: list[bytes], metadata: list[str]):
        """
        Initializes a QuantResponse object.

        Args:
            response (str): The response string received from the miner.
            signature (bytes): The signature associated with the response.
            proofs (list[bytes]): A list of computational proofsfor validating the response.
            metadata (list[str]): Additional metadata related to the response.
        """
        self.response = response
        self.signature = signature
        self.proofs = proofs
        self.metadata = metadata

    def validate(self) -> bool:
        """
        Validates the response proofs as well as the signatures.

        Returns:
            bool: True if the proofs are valid, False otherwise.
        """
        # TODO(developer): Implement validation logic for the proofs
        return True


class QuantSynapse(bt.Synapse):
    """
    A simple protocol representation which uses bt.Synapse as its base.
    This protocol helps in handling request and response communication between
    the miner and the validator.

    Attributes:
    - query: A QuantQuery object representing the input request sent by the validator.
    - response: An optional QuantResponse object which, when filled, represents the response from the miner.
    """
    
    def __init__(self, query: QuantQuery):
        """
        Initializes the QuantSynapse with a given query.

        Args:
        - query (QuantQuery): The query object representing the input request sent by the validator.
        """
        self.query = query
        self.response = None  # Initialize response as None

    # Required request input, filled by sending dendrite caller.
    query: QuantQuery

    # Optional request output, filled by receiving axon.
    response: typing.Optional[QuantResponse] = None

    def set_response(self, response: QuantResponse):
        """
        Sets the response for the QuantSynapse.

        Args:
            response (QuantResponse): The response object to be set.
        """
        self.response = response

    def deserialize(self) -> QuantResponse:
        """
        Deserialize the response. This method retrieves the response from
        the miner in the form of response, deserializes it and returns it
        as the output of the dendrite.query() call.

        Returns:
        - QuantResponse: The deserialized response, which in this case is the value of response.

        Example:
        Assuming a QuantSynapse instance has a response value filled:
        >>> synapse_instance = QuantSynapse(query=QuantQuery("example", "0x123", []))
        >>> synapse_instance.response = QuantResponse("response_data", b'signature', [b'proof1'], [])
        >>> synapse_instance.deserialize()
        QuantResponse("response_data", b'signature', [b'proof1'], [])
        """
        return self.response
