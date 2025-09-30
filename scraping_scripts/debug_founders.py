#!/usr/bin/env python3
"""
Debug script per testare l'import dei founders IFF
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.neo4j_repo import Neo4jRepository
import pandas as pd

def test_person_creation():
    """Test the creation of IFF founders"""
    repo = Neo4jRepository()
    
    # Test con i primi 2 founders che falliscono
    test_founders = [
        {
            'name': 'Marco',
            'surname': 'Ogliengo', 
            'role_type': 'Founder',
            'linkedin_url': 'https://www.linkedin.com/in/mogliengo/',
            'twitter_handle': '',
            'location': '',
            'biography': '',
            'birth_year': '',
            'education': '',
            'previous_experience': '',
            'specialization': '',
            'reputation_score': ''
        },
        {
            'name': 'Francesco',
            'surname': 'Scalambrino',
            'role_type': 'Founder', 
            'linkedin_url': 'https://www.linkedin.com/in/francescoscalambrino/',
            'twitter_handle': '',
            'location': '',
            'biography': '',
            'birth_year': '',
            'education': '',
            'previous_experience': '',
            'specialization': '',
            'reputation_score': ''
        }
    ]
    
    for i, founder in enumerate(test_founders, 1):
        print(f"\n=== Testing Founder {i}: {founder['name']} {founder['surname']} ===")
        
        # Check if person already exists
        query = """
        MATCH (p:Person {name: $name, surname: $surname})
        RETURN p.name, p.surname, p.linkedin_url
        """
        try:
            result = repo.connection.execute_query(query, {'name': founder['name'], 'surname': founder['surname']})
            if result and len(result.records) > 0:
                print(f"❌ Person already exists: {result.records[0]['p.name']} {result.records[0]['p.surname']}")
                print(f"   Existing LinkedIn: {result.records[0]['p.linkedin_url']}")
                print(f"   New LinkedIn: {founder['linkedin_url']}")
            else:
                print(f"✅ Person does not exist yet")
        except Exception as e:
            print(f"❌ Error checking existing person: {e}")
        
        # Try to create
        try:
            success = repo.create_person(founder)
            if success:
                print(f"✅ Successfully created person")
            else:
                print(f"❌ Failed to create person")
        except Exception as e:
            print(f"❌ Exception creating person: {e}")

if __name__ == "__main__":
    test_person_creation()
