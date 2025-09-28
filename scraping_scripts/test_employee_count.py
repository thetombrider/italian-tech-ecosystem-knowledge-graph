#!/usr/bin/env python3
"""
Test per verificare il parsing degli employee count con range
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.csv_importer import CSVImporter
from app.neo4j_repo import Neo4jRepository

def test_employee_count_parsing():
    # Create mock repository (non serve per questo test)
    repo = None
    importer = CSVImporter(repo)
    
    # Test cases
    test_cases = [
        ("11-50", 30),      # (11+50)//2 = 30
        ("1-10", 5),        # (1+10)//2 = 5  
        ("501-1000", 750),  # (501+1000)//2 = 750
        ("25", 25),         # Single number
        ("", None),         # Empty string
        (None, None),       # None value
        ("N/A", None),      # Non-numeric
        ("10-20 employees", 15),  # With text
    ]
    
    print("=== Employee Count Parsing Test ===")
    
    for input_val, expected in test_cases:
        result = importer.parse_employee_count(input_val)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: '{input_val}' -> Output: {result} (Expected: {expected})")
    
    print("\n=== Test del file CSV reale ===")
    # Test with our actual CSV values
    csv_values = ["11-50", "1-10"]
    for val in csv_values:
        result = importer.parse_employee_count(val)
        print(f"CSV value '{val}' -> {result}")

if __name__ == "__main__":
    test_employee_count_parsing()
