"""
Quick test script for the API
"""
import requests

# Test health check
print("Testing health endpoint...")
response = requests.get("http://localhost:8888/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test upload
print("Testing PDF upload...")
with open("OrionTech_Detailed_Report.pdf", "rb") as f:
    files = {"file": ("OrionTech_Detailed_Report.pdf", f, "application/pdf")}
    response = requests.post("http://localhost:8888/upload", files=files)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}\n")
    else:
        print(f"Error: {response.text}\n")

# Test query
print("Testing query...")
query = {
    "question": "What is the net profit margin for OrionTech?"
}
response = requests.post("http://localhost:8888/query", json=query)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"\nQuery: {result['query']}")
    print(f"Plan: {result['plan']}")
    print(f"\nExecutive Summary:\n{result['executive_summary']}")
    print(f"\nAnalysis:\n{result['analysis']}")
    print(f"\nRisk Factors:\n{result['risk_factors']}")
    print(f"\nConfidence: {result['confidence']}")
    print(f"Retry Count: {result['retry_count']}")
    if result.get('computed_metrics'):
        print(f"\nComputed Metrics: {result['computed_metrics']}")
else:
    print(f"Error: {response.text}")
