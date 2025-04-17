<div align="center">

# **BitQuant Subnet by OpenGradient** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

## The Incentivized Internet for AI-Powered Quantitative Analysis <!-- omit in toc -->

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)
</div>

---
- [Introduction](#introduction)
- [BitQuant](#BitQuant)
- [Installation](#installation)
- [Architecture](#architecture)
- [Development](#development)
- [License](#license)
---
## Introduction

OpenGradient's BitQuant Subnet implements a decentralized AI framework for quantitative DeFi analysis on the Bittensor network. Through natural language interfaces, it enables:
- ML-powered market analytics
- Portfolio analysis and optimization
- Risk assessment and trend analysis
- Quantitative strategy evaluation

## BitQuant

The subnet is powered by BitQuant, OpenGradient's AI agent framework for quantitative analysis that provides:
- Real-time market data processing and insights
- Portfolio analysis and optimization
- Price trend and pattern analysis
- Token metrics and risk evaluation
- Risk-reward assessment

## Architecture

The OG BitQuant subnet implements a decentralized quantitative analysis framework through three main components:

### Protocol Layer
- Defines the `QuantSynapse` 
- Handles query/response structures through `QuantQuery` and `QuantResponse`
- Manages message validation and serialization
- Provides the `QuantAPI` for standardized network interaction

### Network Nodes

**Miners**
- Process incoming requests through blacklist and priority checks
- Forward validated queries to BitQuant for processing
- Add response metadata and handle error cases

**Validators**
- Sample random miners for querying
- Forward analysis requests to selected miners
- Calculate response scores through reward function
- Update miner scores in the metagraph

## Installation

### Prerequisites
- Python 3.11+
- Bittensor
- Access to compute resources (see `min_compute.yml`)

For detailed setup instructions, see:
- [Local Development](./docs/running_on_staging.md)
- [Testnet Deployment](./docs/running_on_testnet.md)
- [Mainnet Deployment](./docs/running_on_mainnet.md)

## License
This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2025 BitQuant Subnet by OpenGradient

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
```
