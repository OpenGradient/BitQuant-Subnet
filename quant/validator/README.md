# BitQuant Validator: OpenGradient SDK Setup

A BitQuant validators now may use the OpenGradient SDK for LLM evaluations. This routes all evaluation requests through the decentralized OpenGradient Network.

## Update Instructions

### 1. Pull Latest Code
```bash
cd BitQuant-Subnet
git pull origin Validator
pip install -r requirements.txt
```

## Configuration

### 1. Choose Your Model
Set `LLM_MODEL` to one of the supported models:
```bash
export LLM_MODEL="gemini-2.5-flash-lite"  # Google 
export LLM_MODEL="claude-haiku-4-5-20251001"  
export LLM_MODEL="gpt-4o-mini"  
```

### 2. Set API Key
Provide the API key matching your chosen model:
```bash
# For Google models
export GOOGLE_API_KEY="your_google_api_key"

# For Anthropic models
export ANTHROPIC_API_KEY="your_anthropic_api_key"

# For OpenAI models
export OPENAI_API_KEY="your_openai_api_key"
```

**⚠️ At least ONE API key must be configured**

### 3. Configure OpenGradient Network

#### Get Your OpenGradient Private Key

**Create New Account (Recommended)**
```bash
# Install OpenGradient SDK in a virtual environment
python3 -m venv opengradient-env
source opengradient-env/bin/activate
pip install git+https://github.com/OpenGradient/sdk.git@main

# Run the configuration wizard
opengradient config init
```

The wizard will:
1. Guide you through creating a Model Hub account at https://hub.opengradient.ai/signup
2. Help you create or import an Ethereum-compatible private key
3. Direct you to the Test Faucet for devnet tokens


**Note** ⚠️ SAVE THIS PRIVATE KEY SECURELY!
```

#### Set Environment Variables
```bash
# Required
export OPENGRADIENT_PRIVATE_KEY="your_private_key_here"

# Optional (defaults shown)
export OPENGRADIENT_RPC_URL="http://18.218.115.248:8545"
export OPENGRADIENT_CONTRACT_ADDRESS="0xF78F7d5a7e9f484f0924Cc21347029715bD3B8f4"
```
**⚠️ Security Note:** Never share or commit your private key. Store it securely.

## Quick Start
```bash
# 1. Set model
export LLM_MODEL="gemini-2.5-flash-lite"

# 2. Set API key
export GOOGLE_API_KEY="your_key_here"

# 3. Configure OpenGradient
export OPENGRADIENT_PRIVATE_KEY="your_private_key_here"

# 4. Restart validator
```

## Verification

On successful startup, you should see:
```
✅ OpenGradient SDK client initialized
   Model: gemini-2.5-flash-lite
   Available providers: Google
   Network: http://18.218.115.248:8545
```

During evaluation:
```
🔄 Routing evaluation request through OpenGradient Network...
✅ Evaluation complete: 42/50 → 0.840
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No API keys configured" | Set the API key matching your chosen model |
| "Failed to initialize OpenGradient client" | Verify `OPENGRADIENT_PRIVATE_KEY` is set correctly |
| "Empty response from OpenGradient SDK" | Check network connectivity and RPC URL |

## Resources

- OpenGradient Documentation: https://docs.opengradient.ai/
- OpenGradient GitHub: https://github.com/OpenGradient/sdk
- Model Hub: https://hub.opengradient.ai/
