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
import bittensor as bt  # noqa: E402
from typing import List, Optional, Union, Any, Dict
from template.protocol import QuantSynapse,QuantQuery, QuantResponse
from bittensor.subnets import SubnetsAPI  # noqa: E402


class QuantAPI(SubnetsAPI):
    def __init__(self, wallet: "bt.wallet"):
        super().__init__(wallet)
        TODO: Update UID
        self.netuid = 33
        self.name = "quant"

    def prepare_synapse(self, query: str, userID: str, metadata: list[str]) -> QuantSynapse:
        return QuantSynapse(query=QuantQuery(query, userID, metadata)) 

    def process_responses(self, responses: List[Union["bt.Synapse", Any]]):
        outputs = []
        for response in responses:
            if response.dendrite.status_code != 200:
                continue
            outputs.append(response.response)
        return outputs
