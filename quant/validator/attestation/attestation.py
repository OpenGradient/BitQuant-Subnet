import requests
from typing import Dict
import re
import json
import os
import time
import bittensor as bt

GPU_ATTEST_URL = "http://34.96.84.217:5001/attest/gpu"
GPU_ATTEST_HEADERS = {"Content-Type": "application/json"}

GOLDEN_MEASUREMENTS_PATH = os.path.join(os.path.dirname(__file__), 'golden_measurements.json')
def load_golden_measurements():
    with open(GOLDEN_MEASUREMENTS_PATH, 'r') as f:
        return json.load(f)
GOLDEN_MEASUREMENTS = load_golden_measurements()
SUCCESS_STRINGS = [
    "Attestation report signature verification successful.",
    "Attestation report verification successful.",
    "The runtime measurements are matching with the golden measurements.",
    "GPU is in expected state.",
    "GPU Attestation is Successful."
]

def generate_nonce(epoch_seconds: int = None) -> str:
    """
    Generate a nonce based on the current epoch hour (default) or a user-supplied epoch.
    """
    if epoch_seconds is None:
        epoch_seconds = int(time.time())
    # Use the hour as the nonce (change granularity as needed)
    epoch_hour = epoch_seconds // 3600
    return f"{epoch_hour:016x}"

def retrieve_remote_attestation(nonce: str = None) -> Dict:
    if nonce is None:
        nonce = generate_nonce()
    data = {"nonce": nonce}
    response = requests.post(GPU_ATTEST_URL, headers=GPU_ATTEST_HEADERS, json=data)
    if response.status_code != 200:
        raise RuntimeError("Failed to retrieve remote attestation")
    return parse_gpu_attestation(response.text)

def parse_gpu_attestation(raw_attestation_doc: str) -> Dict:
    # Parse measurement blocks
    measurement_blocks = re.findall(
        r"Measurement Block index : (\d+).*?DMTFSpecMeasurementValue     : ([0-9a-fA-F]+)",
        raw_attestation_doc, re.DOTALL)
    measurements = [block[1] for block in measurement_blocks]

    # Check for all relevant success strings
    checks = {s: (s in raw_attestation_doc) for s in SUCCESS_STRINGS}

    # Overall status
    overall_success = all(checks.values())
    return {
        "measurements": measurements,
        "checks": checks,
        "overall_success": overall_success
    }

def validate_attestation(attestation: Dict) -> bool:
    # Compare measurements to golden
    if attestation["measurements"] != GOLDEN_MEASUREMENTS:
        bt.logging.warning("[Attestation] Measurement mismatch detected.")
        bt.logging.warning(f"[Attestation] Expected measurements: {GOLDEN_MEASUREMENTS}")
        bt.logging.warning(f"[Attestation] Got measurements: {attestation['measurements']}")
        return False
    if not attestation["overall_success"]:
        failed_checks = [k for k, v in attestation.get("checks", {}).items() if not v]
        bt.logging.warning(f"[Attestation] overall_success is False. Failed checks: {failed_checks}")
        return False
    return True
