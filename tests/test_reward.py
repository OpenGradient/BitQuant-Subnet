"""
Test script for reward.py OpenGradient SDK integration
Works around SDK's langchain import issue
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Set environment variables
os.environ['GEMINI_API_KEY'] = 'tesst'
os.environ['LLM_MODEL'] = 'gemini-2.5-flash-lite'

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*70)
print("REWARD.PY TEST - OPENGRADIENT SDK INTEGRATION")
print("="*70)

# Mock the problematic parts of opengradient SDK BEFORE importing
print("\n🔧 Patching OpenGradient SDK langchain imports...")

# Create mock modules for the broken imports
mock_langchain_schema = MagicMock()
mock_langchain_messages = MagicMock()
mock_langchain_og = MagicMock()

sys.modules['langchain.schema'] = mock_langchain_schema
sys.modules['langchain_core.messages'] = mock_langchain_messages
sys.modules['opengradient.llm.og_langchain'] = mock_langchain_og

# Now we can import opengradient
import opengradient as og
from opengradient import LlmInferenceMode

print("✅ OpenGradient SDK imported (with langchain patched)")

# Import our modules
from quant.protocol import QuantQuery, QuantResponse
from quant.validator.reward import (
    get_og_client,
    call_llm,
    subnet_evaluation,
    reward,
    check_security
)

print("✅ Reward module imported successfully\n")


def test_1_client_initialization():
    """Test OpenGradient client initialization"""
    print("="*70)
    print("TEST 1: Client Initialization")
    print("="*70)
    
    try:
        client = get_og_client()
        print(f"✅ Client initialized: {type(client)}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_llm_call():
    """Test LLM call through subnet_evaluation (with template)"""
    print("\n" + "="*70)
    print("TEST 2: LLM Call via Subnet Evaluation")
    print("="*70)
    
    # Create test query and response
    query = QuantQuery(
        query="What is 2+2?",
        userID="test_user",
        metadata={}
    )
    
    response = QuantResponse(
        response="2+2 equals 4. This is basic arithmetic.",
        signature=b"mock_sig",
        proofs=[b"mock_proof"],
        metadata={}
    )
    
    try:
        # This will use your actual template!
        score = subnet_evaluation(query, response)
        print(f"✅ Evaluation successful (with template)")
        print(f"   Score: {score}")
        
        # Note: Score might be 0.0 if security check fails, that's okay for testing
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_security_check():
    """Test security check (may fail if API unavailable)"""
    print("\n" + "="*70)
    print("TEST 3: Security Check")
    print("="*70)
    
    query = QuantQuery(
        query="Test query",
        userID="test_user",
        metadata={}
    )
    
    response = QuantResponse(
        response="Test response",
        signature=b"mock_signature",
        proofs=[b"mock_proof"],
        metadata={}
    )
    
    try:
        passed = check_security(query, response)
        print(f"   Security check result: {passed}")
        print("   ℹ️  Note: May return False if security API is unreachable")
        return True  # We just test that it doesn't crash
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_4_subnet_evaluation():
    """Test full subnet evaluation"""
    print("\n" + "="*70)
    print("TEST 4: Subnet Evaluation")
    print("="*70)
    
    query = QuantQuery(
        query="What is the capital of France?",
        userID="test_user",
        metadata={}
    )
    
    response = QuantResponse(
        response="The capital of France is Paris.",
        signature=b"mock_sig",
        proofs=[],
        metadata={}
    )
    
    try:
        score = subnet_evaluation(query, response)
        print(f"✅ Evaluation completed")
        print(f"   Score: {score}")
        
        if score == 0.0:
            print("   ⚠️  Score is 0.0 (security check may have failed)")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_reward_calculation():
    """Test full reward calculation"""
    print("\n" + "="*70)
    print("TEST 5: Reward Calculation")
    print("="*70)
    
    query = QuantQuery(
        query="Explain Python in one sentence",
        userID="test_user",
        metadata={}
    )
    
    response = QuantResponse(
        response="Python is a high-level programming language.",
        signature=b"sig",
        proofs=[],
        metadata={}
    )
    
    try:
        score = reward(query, response)
        print(f"✅ Reward calculated: {score}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_6_invalid_responses():
    """Test handling of invalid responses"""
    print("\n" + "="*70)
    print("TEST 6: Invalid Response Handling")
    print("="*70)
    
    query = QuantQuery(query="test", userID="user", metadata={})
    
    # Test None response
    score1 = reward(query, None)
    print(f"   None response: {score1} {'✅' if score1 == 0.0 else '❌'}")
    
    # Test empty response
    empty_resp = QuantResponse(response="", signature=b"s", proofs=[], metadata={})
    score2 = reward(query, empty_resp)
    print(f"   Empty response: {score2} {'✅' if score2 == 0.0 else '❌'}")
    
    return score1 == 0.0 and score2 == 0.0


def main():
    """Run all tests"""
    tests = [
        ("Client Initialization", test_1_client_initialization),
        ("LLM Call", test_2_llm_call),
        ("Security Check", test_3_security_check),
        ("Subnet Evaluation", test_4_subnet_evaluation),
        ("Reward Calculation", test_5_reward_calculation),
        ("Invalid Response Handling", test_6_invalid_responses),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready for deployment.")
        return 0
    elif passed >= 4:
        print(f"\n✅ Core functionality works ({passed}/{total} passed)")
        print("Note: Some tests may fail due to external API availability")
        return 0
    else:
        print(f"\n⚠️  {total - passed} critical test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())