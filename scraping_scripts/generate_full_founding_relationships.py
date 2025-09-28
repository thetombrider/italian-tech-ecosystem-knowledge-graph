#!/usr/bin/env python3
"""
Generate complete founding relationships CSV with separated name and surname
"""

import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_founding_relationships_csv():
    """Generate founding relationships CSV with separated name and surname"""
    
    # Read the existing founders and founding relationships data
    try:
        founders_df = pd.read_csv('c14_complete_ecosystem_founders.csv', sep='|')
        logger.info(f"Loaded {len(founders_df)} founders")
        
        # Read the backup founding relationships (with full names)
        backup_df = pd.read_csv('backup/c14_complete_ecosystem_founding_relationships.csv', sep='|')
        logger.info(f"Loaded {len(backup_df)} founding relationships from backup")
        
        # Create a mapping from full name to (name, surname)
        name_mapping = {}
        for _, founder in founders_df.iterrows():
            full_name = f"{founder['name']} {founder['surname']}".strip()
            name_mapping[full_name] = (founder['name'], founder['surname'])
        
        logger.info(f"Created name mapping for {len(name_mapping)} founders")
        
        # Process the founding relationships
        new_relationships = []
        
        for _, rel in backup_df.iterrows():
            person_full_name = rel['person_name']
            
            # Try to find the mapping
            if person_full_name in name_mapping:
                name, surname = name_mapping[person_full_name]
            else:
                # Fallback: split the name manually
                name_parts = person_full_name.strip().split()
                name = name_parts[0] if name_parts else ""
                surname = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ""
                logger.warning(f"No mapping found for '{person_full_name}', using fallback split")
            
            # Clean role to avoid CSV issues with pipe separator
            role = str(rel['role']).replace('|', ' & ') if pd.notna(rel['role']) else ""
            
            new_relationship = {
                'person_name': name,
                'person_surname': surname,
                'startup_name': rel['startup_name'],
                'role': role,
                'founding_date': rel['founding_date'] if pd.notna(rel['founding_date']) else '',
                'equity_percentage': rel['equity_percentage'] if pd.notna(rel['equity_percentage']) else '',
                'is_current': rel['is_current'] if pd.notna(rel['is_current']) else 'true',
                'exit_date': rel['exit_date'] if pd.notna(rel['exit_date']) else ''
            }
            
            new_relationships.append(new_relationship)
        
        # Create new DataFrame
        new_df = pd.DataFrame(new_relationships)
        
        # Save to CSV
        output_file = 'c14_complete_ecosystem_founding_relationships.csv'
        new_df.to_csv(output_file, sep='|', index=False)
        
        logger.info(f"Generated {len(new_relationships)} founding relationships in {output_file}")
        
        # Show some statistics
        print(f"\nStatistics:")
        print(f"Total founding relationships: {len(new_relationships)}")
        print(f"Unique founders: {new_df['person_name'].nunique()}")
        print(f"Unique startups: {new_df['startup_name'].nunique()}")
        
        # Show first few rows
        print(f"\nFirst 3 rows:")
        print(new_df.head(3).to_string())
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error generating founding relationships CSV: {e}")
        return None

if __name__ == "__main__":
    generate_founding_relationships_csv()
