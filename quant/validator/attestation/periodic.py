import threading
import time
import bittensor as bt
from .attestation import retrieve_remote_attestation, validate_attestation, generate_nonce

def periodic_attestation_check(interval_seconds: int = 3600):
    """
    Runs attestation validation at the top of every hour (default) in a background thread.
    """
    def _job():
        while True:
            now = time.time()
            # Calculate seconds until the next hour
            seconds_until_next_hour = 3600 - (int(now) % 3600)
            bt.logging.info(f"Sleeping {seconds_until_next_hour}s until next attestation check...")
            time.sleep(seconds_until_next_hour)
            try:
                nonce = generate_nonce()
                bt.logging.info(f"Running attestation check at epoch hour nonce: {nonce}")
                attestation = retrieve_remote_attestation(nonce)
                if validate_attestation(attestation):
                    bt.logging.info("[Attestation] SUCCESS")
                else:
                    bt.logging.warning("[Attestation] FAILURE")
            except Exception as e:
                bt.logging.error(f"[Attestation] ERROR: {e}")
    thread = threading.Thread(target=_job, daemon=True)
    thread.start()

if __name__ == "__main__":
    bt.logging.info("Starting periodic attestation check (every hour)...")
    periodic_attestation_check()
    while True:
        time.sleep(60)
