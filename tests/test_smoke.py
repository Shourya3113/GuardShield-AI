import sys
import pytest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

def test_data_splits_exist():
    splits_dir = BASE_DIR / "data" / "processed" / "splits_v3"
    assert splits_dir.exists(), f"Splits directory {splits_dir} does not exist."
    
    expected_files = [
        "test_in_distribution.json",
        "test_out_of_distribution.json",
        "fever_eval_400.json",
        "halueval_eval_400.json"
    ]
    for filename in expected_files:
        filepath = splits_dir / filename
        assert filepath.exists(), f"Expected split file {filename} is missing."
        assert filepath.stat().st_size > 0, f"Split file {filename} is empty."

def test_streaming_entropy_engine():
    from src.streaming_entropy_engine import StreamingEntropyEngine
    engine = StreamingEntropyEngine(spike_threshold=1.20, consecutive_spike_limit=2)
    
    # 1. Deterministic / confident distribution -> Low entropy
    res_low = engine.process_token("Paris", [0.95, 0.03, 0.02])
    assert res_low["entropy"] < 1.20
    assert not res_low["should_terminate"]
    assert res_low["status"] == "OK"
    
    # 2. Uniform / uncertain distribution -> High entropy
    res_high = engine.process_token("quantum", [0.34, 0.33, 0.33])
    assert res_high["entropy"] > 1.20
    assert res_high["status"] == "WARN_SPIKE"
    
    # Second consecutive spike -> Early termination
    res_high_2 = engine.process_token("astronauts", [0.35, 0.35, 0.30])
    assert res_high_2["should_terminate"]

def test_fastapi_proxy_health():
    from fastapi.testclient import TestClient
    from src.proxy_server import app
    
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert data.get("service") == "GuardShield AI Sidecar Proxy"

if __name__ == "__main__":
    test_data_splits_exist()
    test_streaming_entropy_engine()
    test_fastapi_proxy_health()
    print("All smoke tests passed successfully!")
