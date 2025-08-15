# Running Subnet on Testnet

This tutorial shows how to use the Bittensor testnet to create a subnet and run your incentive mechanism on it. 

**IMPORTANT:** We strongly recommend that you first run [Running Subnet Locally](running_on_staging.md) before running on the testnet. Incentive mechanisms running on the testnet are open to anyone, and although these mechanisms on testnet do not emit real TAO, they cost you test TAO which you must create. 

**DANGER**
- Do not expose your private keys.
- Only use your testnet wallet.
- Do not reuse the password of your mainnet wallet.
- Make sure your incentive mechanism is resistant to abuse. 

## Prerequisites

Before proceeding further, make sure that you have installed Bittensor. See the below instructions:

- [Install `bittensor`](https://github.com/opentensor/bittensor#install).

After installing `bittensor`, proceed as below:

## 1. Install BitQuant-Subnet

**NOTE: Skip this step if** you already did this during local testing and development.

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
```

**Note**: Running a miner node requires substantially higher compute requirements due to the local running of the BitQuant agent. Setup instructions can be found https://github.com/OpenGradient/BitQuant

## 2. Create wallets 

Create wallets for subnet owner, subnet validator and for subnet miner.
  
This step creates local coldkey and hotkey pairs for your three identities: subnet owner, subnet validator and subnet miner. 

The owner will create and control the subnet. The owner must have at least 100 testnet TAO before the owner can run next steps. 

The validator and miner will be registered to the subnet created by the owner. This ensures that the validator and miner can run the respective validator and miner scripts.

Create a coldkey for your owner wallet:

```bash
btcli wallet new_coldkey --wallet.name owner
```

Create a coldkey and hotkey for your miner wallet:

```bash
btcli wallet new_coldkey --wallet.name miner
```

and

```bash
btcli wallet new_hotkey --wallet.name miner --wallet.hotkey default
```

Create a coldkey and hotkey for your validator wallet:

```bash
btcli wallet new_coldkey --wallet.name validator
```

and

```bash
btcli wallet new_hotkey --wallet.name validator --wallet.hotkey default
```

## 3. (Optional) Get faucet tokens
   
Faucet is disabled on the testnet. Hence, if you don't have sufficient faucet tokens, ask the [Bittensor Discord community](https://discord.com/channels/799672011265015819/830068283314929684) for faucet tokens.

## 4. Register keys

This step registers your subnet validator and subnet miner keys to the subnet, giving them the **first two slots** on the subnet.

Register your miner key to the subnet:

```bash
btcli subnet register --netuid 341 --subtensor.network test --wallet.name miner --wallet.hotkey default
```

Follow the below prompts:

```bash
>> Enter netuid [1] (1): # Enter netuid 1 to specify the subnet you just created.
>> Continue Registration?
  hotkey:     ...
  coldkey:    ...
  network:    finney [y/n]: # Select yes (y)
>> ✅ Registered
```

Next, register your validator key to the subnet:

```bash
btcli subnet register --netuid 341 --subtensor.network test --wallet.name validator --wallet.hotkey default
```

Follow the prompts:

```bash
>> Enter netuid [1] (1): # Enter netuid 1 to specify the subnet you just created.
>> Continue Registration?
  hotkey:     ...
  coldkey:    ...
  network:    finney [y/n]: # Select yes (y)
>> ✅ Registered
```

## 5. Check that your keys have been registered

This step returns information about your registered keys.

Check that your validator key has been registered:

```bash
btcli wallet overview --wallet.name validator --subtensor.network test
```

The above command will display the below:

```bash
Subnet: 1                                                                                                                                                                
COLDKEY  HOTKEY   UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON  HOTKEY_SS58                    
miner    default  0      True   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000                14  none  5GTFrsEQfvTsh3WjiEVFeKzFTc2xcf…
1        1        2            τ0.00000  0.00000  0.00000    0.00000    0.00000    0.00000           ρ0  0.00000                                                         
                                                                          Wallet balance: τ0.0         
```

Check that your miner has been registered:

```bash
btcli wallet overview --wallet.name miner --subtensor.network test
```

The above command will display the below:

```bash
Subnet: 1                                                                                                                                                                
COLDKEY  HOTKEY   UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON  HOTKEY_SS58                    
miner    default  1      True   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000                14  none  5GTFrsEQfvTsh3WjiEVFeKzFTc2xcf…
1        1        2            τ0.00000  0.00000  0.00000    0.00000    0.00000    0.00000           ρ0  0.00000                                                         
                                                                          Wallet balance: τ0.0   
```

## 6. Run subnet miner and subnet validator

Run the subnet miner:

```bash
python neurons/miner.py --netuid 341 --subtensor.network test --wallet.name miner --wallet.hotkey default --logging.debug
```

You will see the below terminal output:

```bash
>> 2023-08-08 16:58:11.223 |       INFO       | Running miner for subnet: 1 on network: ws://127.0.0.1:9946 with config: ...
```

Next, run the subnet validator:

```bash
python neurons/validator.py --netuid 341 --subtensor.network test --wallet.name validator --wallet.hotkey default --logging.debug
```

You will see the below terminal output:

```bash
>> 2023-08-08 16:58:11.223 |       INFO       | Running validator for subnet: 1 on network: ws://127.0.0.1:9946 with config: ...
```


## 7. Get emissions flowing

Register to the root network using the `btcli`:

```bash
btcli root register --subtensor.network test
```

Then set your weights for the subnet:

```bash
btcli root weights --subtensor.network test
```

## 8. Stopping your nodes

To stop your nodes, press CTRL + C in the terminal where the nodes are running.
