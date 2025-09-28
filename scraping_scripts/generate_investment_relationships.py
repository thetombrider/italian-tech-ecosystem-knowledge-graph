#!/usr/bin/env python3
"""
Generate complete investment relationships CSV from backup
"""

import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_investment_relationships_csv():
    """Generate investment relationships CSV from backup"""
    
    try:
        # Read the backup investment relationships
        backup_df = pd.read_csv('backup/c14_complete_ecosystem_investment_relationships.csv', sep='|')
        logger.info(f"Loaded {len(backup_df)} investment relationships from backup")
        
        # Clean the data if needed
        backup_df = backup_df.fillna('')
        
        # Save to current location
        output_file = 'c14_complete_ecosystem_investment_relationships.csv'
        backup_df.to_csv(output_file, sep='|', index=False)
        
        logger.info(f"Generated {len(backup_df)} investment relationships in {output_file}")
        
        # Show some statistics
        print(f"\nStatistics:")
        print(f"Total investment relationships: {len(backup_df)}")
        print(f"Unique investors: {backup_df['investor_name'].nunique()}")
        print(f"Unique startups: {backup_df['startup_name'].nunique()}")
        
        # Show first few rows
        print(f"\nFirst 3 rows:")
        print(backup_df.head(3).to_string())
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error generating investment relationships CSV: {e}")
        return None

if __name__ == "__main__":
    generate_investment_relationships_csv()
