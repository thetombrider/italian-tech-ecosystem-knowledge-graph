#!/usr/bin/env python3
"""
Debug script per verificare i dati estratti dallo scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.c14_scraper import C14Scraper

def debug_scraper():
    scraper = C14Scraper(delay=0.5)
    
    # Test con 4books
    startup_data = scraper.scrape_startup_details("https://www.c14.so/2e45ff9b-d40d-431c-ba1c-25824eaa9174", "4books")
    
    if startup_data:
        print("=== Startup Data Debug ===")
        print(f"Name: '{startup_data.name}'")
        print(f"Description: '{startup_data.description[:100]}...'")
        print(f"Website: '{startup_data.website}'")
        print(f"Location: '{startup_data.location}'")
        print(f"Foundation Date: '{startup_data.foundation_date}'")
        print(f"Team Size: '{startup_data.team_size}'")
        print(f"Funding Stage: '{startup_data.funding_stage}'")
        print(f"Amount Raised: '{startup_data.amount_raised}'")
        print(f"Sectors: {startup_data.sectors}")
    else:
        print("Failed to scrape startup data")

if __name__ == "__main__":
    debug_scraper()
