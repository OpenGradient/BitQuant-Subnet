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
import argparse
import traceback
import bittensor as bt
from typing import List, Optional
from pprint import pprint

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the QuantAPI
try:
    print("Attempting to import QuantAPI...")
    from quant.api.quantapi import QuantAPI
    from quant.protocol import QuantResponse, QuantQuery, QuantSynapse
    print("Successfully imported QuantAPI")
except Exception as e:
    print(f"Error importing QuantAPI: {e}")
    traceback.print_exc()
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the QuantAPI functionality")
    parser.add_argument("--netuid", type=int, default=2, help="The netuid of the subnet to query")
    parser.add_argument("--wallet.name", type=str, default="default", help="The name of the wallet to use")
    parser.add_argument("--wallet.hotkey", type=str, default="default", help="The hotkey of the wallet to use")
    parser.add_argument("--subtensor.network", type=str, default="finney", help="The network to connect to")
    parser.add_argument("--sample_size", type=int, default=3, help="Number of miners to query")
    parser.add_argument("--timeout", type=float, default=12.0, help="Query timeout in seconds")
    parser.add_argument("--logging_debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--specific_uid", type=int, help="Specific UID to query (overrides sample_size)")
    
    return parser.parse_args()

def display_response(index: int, response: QuantResponse):
    """Display a formatted response."""
    print(f"\n--- Response {index+1} ---")
    print(f"Content: {response.response}")
    try:
        sig_preview = response.signature[:10].hex() if response.signature else "None"
        print(f"Signature: {sig_preview}... ({len(response.signature) if response.signature else 0} bytes)")
    except:
        print(f"Signature: Error displaying signature")
    
    print(f"Proofs: {len(response.proofs) if response.proofs else 0} provided")
    if response.metadata:
        print(f"Metadata: {response.metadata}")
    print("-" * 50)

def test_query(quant_api: QuantAPI, args, query: str, user_id: str, metadata: dict):
    """Test a single query and return the responses."""
    try:
        print(f"\nSubmitting query: '{query}'")
        print(f"User ID: {user_id}")
        
        # Convert metadata list to dictionary if it's a list
        if isinstance(metadata, list):
            metadata = {item: True for item in metadata}
            
        print(f"Metadata: {metadata}")
        
        # Check if the API is connected
        if quant_api.metagraph is None:
            print("WARNING: Metagraph is None, attempting to reconnect...")
            quant_api.connect(bt.subtensor(network=getattr(args, "subtensor.network")))
        
        # Show metagraph info
        active_axons = sum(1 for axon in quant_api.metagraph.axons if axon is not None)
        print(f"Active axons in metagraph: {active_axons}/{len(quant_api.metagraph.axons)}")
        
        # Get uids to query
        if args.specific_uid is not None:
            # Use the specific UID
            if args.specific_uid < 0 or args.specific_uid >= len(quant_api.metagraph.axons):
                print(f"ERROR: Specific UID {args.specific_uid} is out of range")
                return []
                
            # Check if the specific UID has a valid axon
            if quant_api.metagraph.axons[args.specific_uid] is None or not quant_api._is_axon_valid(quant_api.metagraph.axons[args.specific_uid]):
                print(f"ERROR: Axon for specific UID {args.specific_uid} is invalid")
                return []
                
            uids = [args.specific_uid]
            print(f"Using specific UID: {args.specific_uid}")
        else:
            # Use sample_size
            print(f"Sample size: {args.sample_size}")
            uids = quant_api.get_uids(k=args.sample_size)
            print(f"Selected UIDs: {uids}")
        
        if not uids:
            print("WARNING: No UIDs were selected, returning empty list")
            return []
        
        print(f"Timeout: {args.timeout} seconds")
        
        # Start timing
        start_time = time.time()
        
        # Submit the query
        print("Sending query to network...")
        responses = quant_api.query(
            uids=uids,
            query=query,
            userID=user_id,
            metadata=metadata,
            timeout=args.timeout
        )
        
        # End timing
        elapsed = time.time() - start_time
        
        print(f"Received {len(responses)} raw responses from dendrite in {elapsed:.2f} seconds")
        
        # Process the responses
        processed_outputs = quant_api.process_responses(responses)
        
        print(f"Processed into {len(processed_outputs)} valid response objects")
        
        # Display the responses
        for i, output in enumerate(processed_outputs):
            display_response(i, output)
            
        return processed_outputs
        
    except Exception as e:
        print(f"Error during query: {e}")
        traceback.print_exc()
        return []

def main():
    """Main function to test the QuantAPI."""
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    if args.logging_debug:
        bt.logging.set_debug(True)
    
    print("Initializing QuantAPI test...")
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
        
        # Update netuid based on command line args
        QuantAPI.netuid = args.netuid
        print(f"Setting netuid to {args.netuid}")
        
        # Initialize the QuantAPI and connect to the network
        print("Initializing QuantAPI...")
        quant_api = QuantAPI(wallet=wallet)
        
        print("Connecting QuantAPI to network...")
        quant_api.connect(subtensor=subtensor)
        
        # Verify that metagraph is loaded
        if quant_api.metagraph is None:
            raise ValueError("Metagraph failed to initialize")
            
        print(f"Metagraph loaded with {len(quant_api.metagraph.hotkeys)} hotkeys")
        
        # Define test queries
        test_queries = [
            {
                "query": "What is the current market cap of Bitcoin?",
                "user_id": wallet.hotkey.ss58_address,
                "metadata": {"topics": ["crypto", "market_data", "bitcoin"]}
            },
            {
                "query": "What is the trading volume of Ethereum in the last 24 hours?",
                "user_id": wallet.hotkey.ss58_address,
                "metadata": {"topics": ["crypto", "volume", "ethereum", "24h"]}
            }
        ]
        
        # Run tests for each query
        results = []
        for i, test_query_data in enumerate(test_queries):
            print(f"\n=== Running test query {i+1}/{len(test_queries)} ===")
            result = test_query(
                quant_api, 
                args, 
                test_query_data["query"], 
                test_query_data["user_id"], 
                test_query_data["metadata"]
            )
            results.append(result)
            
            # Add a small delay between queries
            if i < len(test_queries) - 1:
                time.sleep(2)
        
        # Summary
        print("\n=== Test Summary ===")
        for i, (query_data, result) in enumerate(zip(test_queries, results)):
            print(f"Query {i+1}: '{query_data['query']}' - {len(result)} responses")
        
        print("QuantAPI test completed successfully!")
        
    except Exception as e:
        print(f"Error initializing or running QuantAPI: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 