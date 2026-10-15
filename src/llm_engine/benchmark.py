"""
Internal LLM Engine Benchmark & Verification Suite
Tests multi-object entity resolution, schema linking, parent-child relationship traversal,
and dual SOQL & openCypher query synthesis.
"""

import sys
import json
from pathlib import Path

# Add src to sys.path
from llm_engine.engine import internal_llm

def run_benchmarks():
    test_suite = [
        # 1. Direct Entity Query with Domain Filter
        {
            "query": "Search All Media Type of Account",
            "expected_entity": "Account",
            "type": "Direct Entity Query"
        },
        # 2. Specific Parent Account Lookup on Contact
        {
            "query": "Get Global Media person",
            "expected_entity": "Contact",
            "type": "Specific Parent Account Lookup"
        },
        # 3. Cross-Field Media Resolution on Contact
        {
            "query": "media related person",
            "expected_entity": "Contact",
            "type": "Cross-Field Contact Resolution"
        },
        # 4. Cross-Entity Relational Domain Query on Opportunity
        {
            "query": "Opportunity of Media",
            "expected_entity": "Opportunity",
            "type": "Cross-Entity Relational Domain Query"
        },
        # 5. Opportunity with stage constraint
        {
            "query": "Closed Won deals > 50000",
            "expected_entity": "Opportunity",
            "type": "Opportunity Stage & Amount"
        },
        # 6. Lead status constraint
        {
            "query": "Qualified leads in Media",
            "expected_entity": "Lead",
            "type": "Lead Status & Industry"
        },
        # 7. Open Lead status query
        {
            "query": "open lead",
            "expected_entity": "Lead",
            "type": "Lead Open Status"
        },
        # 8. Open Deals query (IsClosed = false)
        {
            "query": "open deals",
            "expected_entity": "Opportunity",
            "type": "Open Pipeline Deals"
        },
        # 9. Active Account query
        {
            "query": "active account",
            "expected_entity": "Account",
            "type": "Active Account Lifecycle"
        },
        # 10. Pure Entity Query (Company -> Account)
        {
            "query": "company",
            "expected_entity": "Account",
            "type": "Pure Entity Retrieval"
        },
        # 11. Open Pipeline query (Opportunity IsClosed = false)
        {
            "query": "open pipeline",
            "expected_entity": "Opportunity",
            "type": "Open Pipeline Resolution"
        }
    ]

    print("=" * 80)
    print("INTERNAL LOCAL LLM ENGINE (Internal-CRM-LLM-v1.3) - BENCHMARK & VERIFICATION")
    print("=" * 80)

    all_passed = True
    for idx, test in enumerate(test_suite, 1):
        q = test["query"]
        res = internal_llm.generate_query(q)
        sobject = res["sobject"]
        soql = res["soql"]
        cypher = res["cypher"]
        telemetry = res["llm_telemetry"]
        
        passed = sobject == test["expected_entity"]
        if not passed:
            all_passed = False

        status = "PASSED" if passed else "FAILED"
        print(f"[{idx}] {status} | Type: {test['type']}")
        print(f"    Input:      '{q}'")
        print(f"    Entity:     {sobject} (Confidence: {telemetry['confidence_score'] * 100:.1f}%)")
        print(f"    Latency:    {telemetry['inference_time_ms']} ms | Tokens: {telemetry['tokens_processed']}")
        print(f"    Slots:      {telemetry['slots_extracted']}")
        print(f"    SOQL:       {soql}")
        print(f"    openCypher: {cypher}")
        print("-" * 80)

    print(f"BENCHMARK RESULT: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    return all_passed

if __name__ == "__main__":
    success = run_benchmarks()
    sys.exit(0 if success else 1)
