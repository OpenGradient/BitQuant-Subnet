<div align="center">

![BitQuant Banner](docs/Banner2.png)

# **Subnet 15: BitQuant Subnet** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

## The Incentivized Network for AI-Powered Quantitative Analysis <!-- omit in toc -->

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/subnets/15/chart) • [Website](https://bitquant.io)
</div>

---
- [Setup](#setup)
  - [Validator Setup](#validator-setup)
  - [Miner Setup](#miner-setup)
  - [Troubleshooting FAQ](#troubleshooting-faq)
- [Introduction](#introduction)
- [BitQuant](#bitquant)
- [Architecture](#architecture)
- [Installation](#installation)
- [License](#license)
- [Appendix](#appendix)
---

## Setup

### Validator Setup

```bash
# Install Python3.13 and Python3.13 tools on your OS
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev pkg-config

# Clone BitQuant-Subnet Repository and checkout Validator Branch
git clone https://github.com/OpenGradient/BitQuant-Subnet
cd BitQuant-Subnet
git checkout Validator

# Optional: Create Python Virtual Environment (Best Practice)
python3.13 -m venv venv
source venv/bin/activate

# Install Requirements
pip install -r requirements.txt
pip install -e .

# Set up customized environment variables in .env, or fall back to defaults
cp .env.example .env

# Run the Validator with your Bittensor Wallet setup
python neurons/validator.py --netuid 15 --subtensor.network finney --wallet.name validator --wallet.hotkey default --logging.debug
```

### Miner Setup

```bash
# Install Python3.13 and Python3.13 tools on your OS
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev pkg-config

# Clone BitQuant-Subnet Repository and BitQuant submodule
git clone --branch Miner --recursive https://github.com/OpenGradient/BitQuant-Subnet
cd BitQuant-Subnet

# Optional: Create Python Virtual Environment (Best Practice)
python3.13 -m venv venv
source venv/bin/activate

# Install Requirements
pip install -r requirements.txt
pip install -e .

# Setup all the environment variables in .env
cp .env.example .env

# Run the Miner with your Bittensor Wallet setup
python neurons/miner.py --netuid 15 --subtensor.network finney --wallet.name miner --wallet.hotkey default --logging.debug
```

### Troubleshooting FAQ

**Note**: This repository requires Python3.13 and Python3.13 tools

1. **Any 'ModuleNotFoundError'**
   - Make sure you ran both `pip install -r requirements.txt` and `pip install -e .` and `git submodule update --init --recursive`

2. **ERROR: Could not find a version that satisfies the requirement bittensor==9.2.0**
   - Make sure you're using Python3.13 and you update Pip

---

## Introduction

OpenGradient's BitQuant Subnet implements a decentralized AI framework for quantitative DeFi analysis on the Bittensor network. Through natural language interfaces, it enables:
- ML-powered market analytics
- Portfolio analysis and optimization
- Risk assessment and trend analysis
- Quantitative strategy evaluation

### High-Level Goals
- Democratize access to advanced quantitative analytics for DeFi and crypto markets
- Incentivize high-quality AI agents to provide real-time, actionable insights
- Enable composable, on-chain quantitative strategies and risk metrics
- Foster a robust ecosystem for decentralized, AI-powered financial intelligence

The subnet is powered by BitQuant, OpenGradient's AI agent framework for quantitative analysis that provides:
- Real-time market data processing and insights
- Portfolio analysis and optimization
- Price trend and pattern analysis
- Token metrics and risk evaluation
- Risk-reward assessment

## BitQuant
BitQuant is an agentic framework for digital asset analytics and DeFi strategy, enabling users to analyze tokens, DeFi pools, and portfolio risk with advanced on-chain and off-chain data.

**Agent Capabilities:**
- Pool Discovery
- Token Search
- TVL Analytics
- Price Trend Analysis
- Drawdown Calculation
- Portfolio Volatility
- Wallet Analytics
- Trending Tokens
- Token Risk Evaluation
- Top Holders Lookup

**Example Queries:**
- "Find all Solana pools I can invest in with my wallet’s tokens and show their historical TVL."
- "Analyze the price trend and calculate the max drawdown for SOL over the last 90 days."
- "Evaluate my wallet’s portfolio volatility and identify the riskiest token holding."
- "Search for trending tokens across X chain and display their top holders."
- "Compare historical global TVL and chain-specific TVL for Ethereum and Solana."

> **Try it live:** [bitquant.io](https://bitquant.io)

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
- Python 3.13
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

## Appendix
#### BitQuant Example Questions

![BitQuant UI](https://github.com/OpenGradient/public_images/blob/main/bitquant-ui.png?raw=true)
![BitQuant Question Example 3](https://raw.githubusercontent.com/OpenGradient/public_images/fbd27e6119f3157f5682afe2217054504c5abe8d/bitquant-3.png)
![BitQuant Question Example](https://github.com/OpenGradient/public_images/blob/main/bitquant-1.png?raw=true)
![BitQuant Question Example 2](https://github.com/OpenGradient/public_images/blob/main/bitquant-2.png?raw=true)
