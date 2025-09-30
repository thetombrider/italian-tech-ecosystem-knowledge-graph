#!/usr/bin/env python3
"""
Test rapido per verificare che l'app possa processare il file CDP fund relationships
"""

import sys
import os
sys.path.append('/Users/tommy/Progetti Python/italian_tech_ecosystem_graph')

import pandas as pd
from app.csv_importer import CSVImporter
from app.neo4j_repo import Neo4jRepository, Neo4jConnection

def test_cdp_file():
    print("🧪 Test file CDP fund relationships...")
    
    # Trova il file corretto
    script_dir = '/Users/tommy/Progetti Python/italian_tech_ecosystem_graph/scraping_scripts'
    test_file = None
    
    for file in os.listdir(script_dir):
        if file.startswith('cdp_venture_capital_fund_relationships_fixed_') and file.endswith('.csv'):
            test_file = os.path.join(script_dir, file)
            break
    
    if not test_file:
        print("❌ File CDP non trovato!")
        return
    
    print(f"📁 File da testare: {os.path.basename(test_file)}")
    
    # Leggi il file
    try:
        df = pd.read_csv(test_file, delimiter='|')
        print(f"✅ File letto: {len(df)} righe, {len(df.columns)} colonne")
        print(f"📋 Colonne: {list(df.columns)}")
        
        # Mostra primi dati
        print("\n🔍 Prime 3 righe:")
        for i, row in df.head(3).iterrows():
            print(f"  {i+1}: {row['investor_name']} ({row['investor_type']}) → {row['fund_name']} [{row['relationship_type']}]")
        
        # Test validazione (senza connessione Neo4j)
        print("\n🔍 Test validazione...")
        
        # Simula importer (senza connessione reale)
        class MockRepo:
            pass
        
        importer = CSVImporter(MockRepo())
        validation_errors = importer.validate_relationship_csv(df, 'PARTICIPATED_IN')
        
        if validation_errors:
            print("❌ Errori di validazione:")
            for error in validation_errors:
                print(f"  • {error}")
        else:
            print("✅ Validazione OK!")
        
        # Test auto-detect
        print("\n🔍 Test auto-detection...")
        first_row = df.iloc[0]
        detected_type = importer._detect_relationship_type(first_row)
        print(f"Tipo rilevato: {detected_type}")
        
        if detected_type == 'PARTICIPATED_IN':
            print("✅ Auto-detection funziona!")
        else:
            print("❌ Auto-detection fallita")
            
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    test_cdp_file()
