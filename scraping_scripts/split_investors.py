#!/usr/bin/env python3
"""
Split investors CSV by type for separate import
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_investors_by_type():
    """Split investors CSV into separate files by type"""
    
    # Read the investors CSV
    df = pd.read_csv('c14_complete_ecosystem_investors.csv', sep='|')
    logger.info(f"Loaded {len(df)} investors")
    
    # Group by type
    types = df['type'].value_counts()
    print("Investor types:")
    print(types)
    
    # Split and save by type
    for investor_type in df['type'].unique():
        type_df = df[df['type'] == investor_type].copy()
        # Remove the type column since it's implicit now
        type_df = type_df.drop('type', axis=1)
        
        filename = f"c14_investors_{investor_type.lower()}.csv" 
        type_df.to_csv(filename, sep='|', index=False)
        logger.info(f"Saved {len(type_df)} {investor_type} to {filename}")
    
    return True

if __name__ == "__main__":
    split_investors_by_type()
