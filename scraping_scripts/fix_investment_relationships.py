#!/usr/bin/env python3
"""
Fix investor types in investment relationships CSV
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_investment_relationships():
    """Fix investor types in investment relationships CSV"""
    
    # Read the investment relationships
    df = pd.read_csv('backup/c14_complete_ecosystem_investment_relationships.csv', sep='|')
    logger.info(f"Loaded {len(df)} investment relationships")
    
    # Fix B4I type
    df.loc[df['investor_name'] == 'B4I - Bocconi for innovation', 'investor_type'] = 'Institution'
    
    # Count changes
    b4i_count = (df['investor_name'] == 'B4I - Bocconi for innovation').sum()
    logger.info(f"Fixed {b4i_count} B4I relationships to Institution type")
    
    # Save corrected CSV
    output_file = 'c14_complete_ecosystem_investment_relationships.csv'
    df.to_csv(output_file, sep='|', index=False)
    
    logger.info(f"Saved corrected investment relationships to {output_file}")
    return output_file

if __name__ == "__main__":
    fix_investment_relationships()
