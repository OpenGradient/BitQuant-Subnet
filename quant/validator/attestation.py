import requests
from typing import Dict
import re

GPU_ATTEST_URL = "http://34.96.84.217:5001/attest/gpu"
GPU_ATTEST_HEADERS = {"Content-Type": "application/json"}
GOLDEN_MEASUREMENTS = [
    # These are the current/golden RIM values from your sample
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
] * 10  # 10 blocks as in your sample
SUCCESS_STRINGS = [
    "Attestation report signature verification successful.",
    "Attestation report verification successful.",
    "driver RIM verification successful.",
    "vbios RIM verification successful.",
    "The runtime measurements are matching with the golden measurements.",
    "GPU is in expected state.",
    "GPU Attestation is Successful."
]

def retrieve_remote_attestation(nonce: str = None) -> Dict:
    data = {"nonce": nonce or "0123456789abcdef0123456789abcdef"}
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
        return False
    if not attestation["overall_success"]:
        return False
    return True
