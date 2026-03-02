#!/usr/bin/env python3
"""
Integration and Performance Testing Script
CCPA Compliance Analyzer v2.0 (Gemini API)
"""

import os
import time
import json
import requests
import sys

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")

HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["X-API-Key"] = API_KEY

print(f"Testing against API URL: {API_URL}")
print(f"Using API Key Auth: {'YES' if API_KEY else 'NO'}")
print("-" * 50)


def test_health():
    """Test the /health endpoint."""
    print("Testing GET /health...")
    start_time = time.time()
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        latency = time.time() - start_time
        if response.status_code == 200:
            print(f"✅ Health check passed ({latency:.2f}s)")
        else:
            print(f"❌ Health check failed with status {response.status_code}: {response.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        sys.exit(1)
    print("-" * 50)


def test_analyze_standard():
    """Test the POST /analyze endpoint with a harmful prompt."""
    print("Testing POST /analyze (Standard Request)...")
    prompt = "We sell customer browsing history to ad networks without providing any opt-out mechanism."
    payload = {"prompt": prompt}
    
    start_time = time.time()
    try:
        response = requests.post(f"{API_URL}/analyze", headers=HEADERS, json=payload, timeout=60)
        latency = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Request succeeded ({latency:.2f}s)")
            
            # Validate SCHEMA
            expected_keys = {"harmful", "articles", "explanation", "referenced_articles"}
            actual_keys = set(data.keys())
            if expected_keys.issubset(actual_keys):
                print(f"✅ Schema validation passed")
            else:
                print(f"❌ Schema validation failed. Missing: {expected_keys - actual_keys}")
            
            # Validate CONTENT
            if data.get("harmful") is True:
                print(f"✅ Correctly identified as harmful")
            else:
                print(f"❌ Incorrectly identified as safe")
                
            print(f"Response Preview: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Request failed with status {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    print("-" * 50)


def test_analyze_stream():
    """Test the GET /analyze/stream endpoint with a safe prompt."""
    print("Testing GET /analyze/stream (SSE Streaming)...")
    prompt = "We provide a clear privacy policy and honor all deletion requests."
    params = {"prompt": prompt}
    
    headers = HEADERS.copy()
    headers["Accept"] = "text/event-stream"
    
    start_time = time.time()
    first_chunk_time = None
    chunks_received = 0
    full_text = ""
    
    try:
        with requests.get(f"{API_URL}/analyze/stream", headers=headers, params=params, stream=True, timeout=60) as response:
            if response.status_code != 200:
                print(f"❌ Stream request failed with status {response.status_code}: {response.text}")
                return

            # Manually parse SSE lines
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    if first_chunk_time is None:
                        first_chunk_time = time.time() - start_time
                    
                    data_str = line[6:] # Strip 'data: '
                    try:
                        data = json.loads(data_str)
                        if "text" in data:
                            chunks_received += 1
                            full_text += data["text"]
                            # Print a dot for each chunk to show progress
                            print(".", end="", flush=True)
                        elif "error" in data:
                            print(f"\n❌ Stream reported error: {data['error']}")
                            break
                    except json.JSONDecodeError:
                        print(f"\n❌ Failed to decode JSON from stream: {data_str}")
            print() # new line after dots
            
            total_latency = time.time() - start_time
            print(f"✅ Stream completed successfully")
            print(f"   Time to first token (TTFT): {first_chunk_time:.2f}s")
            print(f"   Total streaming time:       {total_latency:.2f}s")
            print(f"   Chunks received:            {chunks_received}")
            print(f"   Generated text preview:     {full_text[:100]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Stream request failed: {e}")
    print("-" * 50)


if __name__ == "__main__":
    print("Starting Integration Tests...")
    test_health()
    test_analyze_standard() # Tests the 4-field schema (REQ-03)
    test_analyze_stream()   # Tests SSE streaming (REQ-04)
    print("Tests Complete.")
