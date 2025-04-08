#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
api_test.py - Test script for QuantAPI functionality

This script demonstrates how to use the QuantAPI to submit queries to
the Bittensor quantitative subnet and process the responses.
"""

import os
import sys
import time
import random
import argparse
import traceback
import requests
import bittensor as bt
from typing import List, Optional
from pprint import pprint

# Set environment variables needed for testing
os.environ["SOLANA_WALLET"] = "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin"
os.environ["BT_DISABLE_VERIFICATION"] = "1"  # Disable verification for testing
print(f"SOLANA_WALLET set to: {os.environ['SOLANA_WALLET']}")
print("Bittensor verification disabled for testing")

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the QuantAPI
try:
    print("Attempting to import protocol modules...")
    from quant.protocol import QuantResponse, QuantQuery, QuantSynapse
    from quant.utils.questions import questions  # Import the same question set used by validator
    print("Successfully imported protocol modules")
except Exception as e:
    print(f"Error importing protocol modules: {e}")
    traceback.print_exc()
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the QuantAPI functionality")
    parser.add_argument("--netuid", type=int, default=2, help="The netuid of the subnet to query")
    parser.add_argument("--wallet.name", type=str, default="validator", help="The name of the wallet to use")
    parser.add_argument("--wallet.hotkey", type=str, default="default", help="The hotkey of the wallet to use")
    parser.add_argument("--subtensor.network", type=str, default="finney", help="The network to connect to")
    parser.add_argument("--timeout", type=float, default=60.0, help="Query timeout in seconds")
    parser.add_argument("--logging_debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--specific_uid", type=int, help="Specific UID to query")
    parser.add_argument("--check_agent", action="store_true", help="Check quant agent server connectivity")
    parser.add_argument("--fixed_query", action="store_true", help="Use a fixed query instead of random")
    
    return parser.parse_args()

def display_response(index: int, response):
    """Display a formatted response."""
    print(f"\n--- Response {index+1} ---")
    if hasattr(response, 'response'):
        print(f"Content: {response.response}")
    else:
        print(f"Content: {response}")
    
    if hasattr(response, 'signature'):
        try:
            sig_preview = response.signature[:10].hex() if response.signature else "None"
            print(f"Signature: {sig_preview}... ({len(response.signature) if response.signature else 0} bytes)")
        except:
            print(f"Signature: Error displaying signature")
    
    if hasattr(response, 'proofs'):
        print(f"Proofs: {len(response.proofs) if response.proofs else 0} provided")
    
    if hasattr(response, 'metadata'):
        print(f"Metadata: {response.metadata}")
    
    print("-" * 50)

def check_agent_server():
    """Check if the quant agent server is accessible."""
    try:
        print("Checking quant agent server connectivity...")
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        print(f"Agent server response: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"Error connecting to agent server: {e}")
        print("Make sure the quant agent server is running at http://127.0.0.1:5000")
        return False

def test_validator_style_query(wallet, subtensor, args):
    """Test a query exactly as the validator would do it."""
    print("\n=== Running validator-style test query ===")
    
    # Check agent server if requested
    if args.check_agent:
        check_agent_server()
    
    # Create a dendrite for querying
    dendrite = bt.dendrite(wallet=wallet)
    print(f"Created dendrite with wallet: {wallet}")
    
    # Get metagraph for axons
    metagraph = subtensor.metagraph(netuid=args.netuid)
    print(f"Loaded metagraph with {len(metagraph.axons)} axons")
    
    # Get the specific UID to query
    if args.specific_uid is not None:
        if args.specific_uid < 0 or args.specific_uid >= len(metagraph.axons):
            print(f"ERROR: Specific UID {args.specific_uid} is out of range 0-{len(metagraph.axons)-1}")
            return []
        miner_uids = [args.specific_uid]
    else:
        miner_uids = [0]  # Default to first miner
    
    print(f"Querying miner UIDs: {miner_uids}")
    
    # Get axons for these UIDs
    axons = [metagraph.axons[uid] for uid in miner_uids if metagraph.axons[uid] is not None]
    if not axons:
        print("ERROR: No valid axons found for the specified UIDs")
        return []
    
    # For local testing, update axon IPs to localhost
    if "127.0.0.1" in getattr(args, "subtensor.network") or "localhost" in getattr(args, "subtensor.network"):
        print("Local network detected, updating axon IPs to localhost")
        for axon in axons:
            print(f"Original axon: {axon.ip}:{axon.port}")
            axon.ip = "127.0.0.1"
            print(f"Updated axon: {axon.ip}:{axon.port}")
    
    # Create validator-style metadata (match exactly what the validator sends)
    metadata = {
        "Create_Proof": "True", 
        "Type": "Validator_Test",
        "validator_id": wallet.hotkey.ss58_address,  # Add validator's hotkey as identifier
        "timestamp": str(int(time.time() * 1000000))  # Add timestamp for uniqueness
    }
    
    # Select a query
    if args.fixed_query:
        current_query = "What is the current market cap of Bitcoin?"
    else:
        # Select a random question from the question pool (same as validator)
        current_query = random.choice(questions)
    
    print(f"Query: {current_query}")
    print(f"Metadata: {metadata}")
    print(f"UserID: {os.getenv('SOLANA_WALLET')}")
    
    # Create the synapse with QuantQuery
    synapse = QuantSynapse(
        query=QuantQuery(
            query=current_query,
            userID=os.getenv("SOLANA_WALLET"),
            metadata=metadata
        )
    )
    
    print(f"Sending query to {len(axons)} axons with timeout {args.timeout} seconds...")
    
    # Enable more detailed debugging if requested
    if args.logging_debug:
        print("\nDetailed synapse object:")
        print(f"  Query text: {synapse.query.query}")
        print(f"  UserID: {synapse.query.userID}")
        print(f"  Metadata: {synapse.query.metadata}")
        
        # Print axon details
        for i, axon in enumerate(axons):
            print(f"\nAxon {i+1} details:")
            print(f"  IP: {axon.ip}")
            print(f"  Port: {axon.port}")
            print(f"  Hotkey: {axon.hotkey}")
    
    # This exactly matches how the validator queries miners
    try:
        # Send the query asynchronously
        start_time = time.time()
        responses = dendrite.query(
            axons=axons,
            synapse=synapse,
            timeout=args.timeout,
            deserialize=True
        )
        duration = time.time() - start_time
        
        print(f"Query completed in {duration:.2f} seconds")
        
        if responses is None:
            print("WARNING: Dendrite query returned None")
            return []
            
        print(f"Received {len(responses)} responses")
        
        # Process responses
        for i, response in enumerate(responses):
            print(f"\nResponse from axon {i+1}:")
            display_response(i, response)
        
        return responses
    except Exception as e:
        print(f"Error during query: {e}")
        traceback.print_exc()
        return []

def main():
    """Main function to test the API."""
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    if args.logging_debug:
        bt.logging.set_debug(True)
    
    print("Initializing API test...")
    print(f"Python version: {sys.version}")
    print(f"Bittensor version: {bt.__version__}")
    
    try:
        # Initialize wallet
        print("Initializing wallet...")
        wallet = bt.wallet(name=getattr(args, "wallet.name"), hotkey=getattr(args, "wallet.hotkey"))
        print(f"Using wallet: {wallet}")
        
        # Set up the subtensor connection
        print(f"Connecting to {getattr(args, 'subtensor.network')} network...")
        subtensor = bt.subtensor(network=getattr(args, "subtensor.network"))
        
        # Check if connection is successful by getting chain block
        block = subtensor.get_current_block()
        print(f"Successfully connected to network. Current block: {block}")
        
        # Run validator-style test
        results = test_validator_style_query(wallet, subtensor, args)
        
        # Summary
        print("\n=== Test Summary ===")
        print(f"Received {len(results)} responses")
        
        print("API test completed successfully!")
        
    except Exception as e:
        print(f"Error initializing or running API test: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 