#!/usr/bin/env python3
"""
Test script for CSV import with new structure
"""

import logging
from app.neo4j_repo import Neo4jConnection, Neo4jRepository
from app.csv_importer import CSVImporter
import pandas as pd

logging.basicConfig(level=logging.INFO)

def test_founding_relationships_import():
    """Test import of founding relationships with new structure"""
    
    # Setup connections
    db_conn = Neo4jConnection()
    if not db_conn.connect():
        print("Failed to connect to database")
        return False
        
    repo = Neo4jRepository(db_conn)
    importer = CSVImporter(repo)
    
    # Load test CSV
    print("Loading test CSV...")
    df = pd.read_csv('test_founding_relationships.csv', sep='|')
    print(f"Loaded {len(df)} relationships")
    print("Columns:", list(df.columns))
    print("\nFirst few rows:")
    print(df.head())
    
    # Validate structure
    errors = importer.validate_relationship_csv(df, 'FOUNDED')
    if errors:
        print(f"Validation errors: {errors}")
        return False
    else:
        print("CSV structure validation passed!")
    
    # Try to import relationships
    print("\nImporting relationships...")
    success_count = 0
    total_count = len(df)
    
    for idx, row in df.iterrows():
        try:
            success = importer._create_relationship(row, 'FOUNDED', idx + 1)
            if success:
                success_count += 1
                print(f"✓ Successfully imported relationship {idx + 1}: {row['person_name']} {row['person_surname']} → {row['startup_name']}")
            else:
                print(f"✗ Failed to import relationship {idx + 1}: {row['person_name']} {row['person_surname']} → {row['startup_name']}")
        except Exception as e:
            print(f"✗ Error importing relationship {idx + 1}: {e}")
    
    print(f"\nImport completed: {success_count}/{total_count} relationships imported successfully")
    
    # Close connection
    db_conn.close()
    
    return success_count == total_count

if __name__ == "__main__":
    test_founding_relationships_import()
