"""
Comprehensive test demonstrating all system features
"""
import requests
import json

BASE_URL = "http://localhost:8888"

def print_section(title):
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def test_health():
    print_section("TEST 1: HEALTH CHECK")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_upload_second_pdf():
    print_section("TEST 2: UPLOAD SECOND PDF (VertexRetail)")
    with open("VertexRetail_Detailed_Report.pdf", "rb") as f:
        files = {"file": ("VertexRetail_Detailed_Report.pdf", f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False

def test_query(question, test_name):
    print_section(f"TEST: {test_name}")
    print(f"Question: {question}\n")
    
    query = {"question": question}
    response = requests.post(f"{BASE_URL}/query", json=query)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"📋 PLANNER OUTPUT:")
        print(f"   Intent: {result['plan']['intent']}")
        print(f"   Metrics Required: {result['plan']['metrics_required']}")
        print(f"   Time Range: {result['plan']['time_range']}")
        
        print(f"\n📊 EXECUTIVE SUMMARY:")
        print(f"   {result['executive_summary']}")
        
        print(f"\n🔍 ANALYSIS:")
        analysis_text = result['analysis']
        if len(str(analysis_text)) > 500:
            print(f"   {str(analysis_text)[:500]}...")
        else:
            print(f"   {analysis_text}")
        
        print(f"\n⚠️  RISK FACTORS:")
        risk_text = result['risk_factors']
        if len(str(risk_text)) > 300:
            print(f"   {str(risk_text)[:300]}...")
        else:
            print(f"   {risk_text}")
        
        print(f"\n📈 METRICS:")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Retry Count: {result['retry_count']}")
        print(f"   Final Weight: {result['final_weight']}")
        
        if result.get('computed_metrics'):
            print(f"\n💰 COMPUTED FINANCIAL METRICS:")
            print(f"   {json.dumps(result['computed_metrics'], indent=6)}")
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_history():
    print_section("TEST: QUERY HISTORY")
    response = requests.get(f"{BASE_URL}/history")
    if response.status_code == 200:
        history = response.json()
        print(f"Total queries logged: {history['count']}")
        print("\nRecent queries:")
        for entry in history['history'][-5:]:
            print(f"  • {entry['query'][:60]}... (confidence: {entry['confidence']}, retries: {entry['retry_count']})")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def main():
    print("\n" + "█"*80)
    print("  AGENTIC RAG FINANCIAL ANALYSIS SYSTEM - COMPREHENSIVE TEST")
    print("█"*80)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health
    total_tests += 1
    if test_health():
        tests_passed += 1
    
    # Test 2: Upload second PDF
    total_tests += 1
    if test_upload_second_pdf():
        tests_passed += 1
    
    # Test 3: Ratio Analysis Query
    total_tests += 1
    if test_query(
        "What are the debt ratio and equity ratio for OrionTech?",
        "RATIO ANALYSIS - AGENT PIPELINE TEST"
    ):
        tests_passed += 1
    
    # Test 4: Trend Analysis Query
    total_tests += 1
    if test_query(
        "Analyze the revenue growth trend for OrionTech from 2021 to 2023",
        "TREND ANALYSIS - AGENT PIPELINE TEST"
    ):
        tests_passed += 1
    
    # Test 5: Risk Analysis Query
    total_tests += 1
    if test_query(
        "What are the main financial risks for VertexRetail?",
        "RISK ANALYSIS - MULTI-DOCUMENT TEST"
    ):
        tests_passed += 1
    
    # Test 6: Summarization Query
    total_tests += 1
    if test_query(
        "Summarize the financial position of OrionTech",
        "SUMMARIZATION - COMPREHENSIVE TEST"
    ):
        tests_passed += 1
    
    # Test 7: Query History
    total_tests += 1
    if test_history():
        tests_passed += 1
    
    # Final Summary
    print_section("FINAL RESULTS")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n✅ ALL TESTS PASSED! System is fully operational.")
        print("\n🎯 Key Features Demonstrated:")
        print("   ✓ PDF ingestion and chunking")
        print("   ✓ ChromaDB vector storage and retrieval")
        print("   ✓ 5-agent pipeline (Planner → Retriever → Analyzer → Generator → Critic)")
        print("   ✓ Multiple analysis types (ratio, trend, risk, summarization)")
        print("   ✓ Financial metrics computation")
        print("   ✓ Retry mechanism with weight decay")
        print("   ✓ Query history logging")
        print("   ✓ Multi-document support")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed.")
    
    print("\n" + "█"*80 + "\n")

if __name__ == "__main__":
    main()
