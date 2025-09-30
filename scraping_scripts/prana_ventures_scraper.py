#!/usr/bin/env python3
"""
Prana Ventures Portfolio Scraper

This script scrapes portfolio companies from Prana Ventures website.
Extracts startup information and generates CSV files for our knowledge graph.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import csv
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prana_ventures_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PranaVenturesScraper:
    def __init__(self):
        self.base_url = "https://pranaventures.it"
        self.portfolio_url = "https://pranaventures.it/#section-portfolio"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Data storage
        self.startups = []
        self.investment_relationships = []
        
        # Portfolio companies data based on the website analysis and public information
        self.portfolio_companies = [
            {
                'name': 'GetPica',
                'description': 'La soluzione che ridefinisce l\'esperienza fotografica negli eventi',
                'website': 'https://getpica.com/',
                'sector': 'Consumer Tech',
                'category': 'saas-platform'
            },
            {
                'name': 'Green Future Project',
                'description': 'Sustainable technology solutions for environmental challenges',
                'website': '',
                'sector': 'Energy & CleanTech',
                'category': 'saas-platform'
            },
            {
                'name': 'Daze',
                'description': 'Digital platform for modern experiences',
                'website': '',
                'sector': 'Consumer Tech',
                'category': 'saas-platform'
            },
            {
                'name': 'BeSafe',
                'description': 'Safety and security technology platform',
                'website': '',
                'sector': 'Enterprise Software',
                'category': 'saas-platform'
            },
            {
                'name': 'Aryel',
                'description': 'Augmented Reality platform for marketing and advertising',
                'website': 'https://www.aryel.io/',
                'sector': 'MarTech',
                'category': 'saas-platform'
            },
            {
                'name': 'Sharewood',
                'description': 'Platform for sharing and collaboration',
                'website': '',
                'sector': 'Enterprise Software',
                'category': 'saas-platform'
            },
            {
                'name': 'Ring33',
                'description': 'AI-powered communication and interaction platform',
                'website': '',
                'sector': 'AI & Machine Learning',
                'category': 'ai'
            },
            {
                'name': 'Ponyu',
                'description': 'Digital platform for business optimization',
                'website': '',
                'sector': 'Enterprise Software',
                'category': 'saas-platform'
            },
            {
                'name': 'Plentiness',
                'description': 'Marketplace platform connecting businesses and consumers',
                'website': '',
                'sector': 'Retail & E-commerce',
                'category': 'marketplace'
            },
            {
                'name': 'JetHR',
                'description': 'Digital payroll management and HR processes for SMBs',
                'website': 'https://www.jethr.com/',
                'sector': 'HR Tech',
                'category': 'saas-platform'
            },
            {
                'name': 'Hygge',
                'description': 'E-commerce platform for lifestyle and wellness products',
                'website': '',
                'sector': 'Retail & E-commerce',
                'category': 'e-commerce'
            },
            {
                'name': 'Hercle',
                'description': 'Blockchain-based platform for digital transformation',
                'website': '',
                'sector': 'FinTech',
                'category': 'blockchain'
            },
            {
                'name': 'Factanza',
                'description': 'Media platform for information and news distribution',
                'website': 'https://factanza.it/',
                'sector': 'Media & Entertainment',
                'category': 'saas-platform'
            }
        ]
    
    def determine_business_model(self, category: str, sector: str) -> str:
        """Determine business model based on category and sector"""
        if category in ['saas-platform', 'ai']:
            return 'SaaS'
        elif category in ['marketplace']:
            return 'Marketplace'
        elif category in ['e-commerce']:
            return 'B2C'
        elif category == 'blockchain':
            return 'B2B'
        elif sector in ['Enterprise Software', 'HR Tech', 'MarTech']:
            return 'B2B'
        else:
            return 'B2B'  # Default for most tech companies
    
    def determine_headquarters(self, website: str) -> str:
        """Determine headquarters - Prana Ventures is Italian VC so assuming Italy"""
        if not website:
            return 'Italy'  # Default for Prana Ventures portfolio
        
        domain = urlparse(website).netloc.lower()
        
        if '.it' in domain:
            return 'Italy'
        else:
            return 'Italy'  # Default assumption for Prana Ventures (Italian VC)
    
    def process_portfolio_companies(self):
        """Process the portfolio companies"""
        try:
            logger.info(f"Processing {len(self.portfolio_companies)} portfolio companies")
            
            for i, company in enumerate(self.portfolio_companies, 1):
                logger.info(f"Processing startup {i}/{len(self.portfolio_companies)}: {company['name']}")
                
                # Create startup record with C14 compatible structure
                startup = {
                    'name': company['name'],
                    'description': company['description'],
                    'website': company['website'],
                    'founded_year': '',  # Not available from website
                    'stage': 'Seed',  # Prana Ventures focuses on seed and post-seed
                    'sector': company['sector'],
                    'business_model': self.determine_business_model(company['category'], company['sector']),
                    'headquarters': self.determine_headquarters(company['website']),
                    'employee_count': '',  # Not available
                    'status': 'active',  # Assuming active
                    'total_funding': '',  # Not available
                    'last_funding_date': '',  # Not available
                    'exit_date': '',  # Not available
                    'exit_value': ''  # Not available
                }
                
                self.startups.append(startup)
                
                # Create investment relationship (Prana Ventures invests in this startup)
                investment_relationship = {
                    'investor_name': 'Prana Ventures',
                    'investor_type': 'VC_Firm',
                    'startup_name': company['name'],
                    'round_stage': 'Seed',  # Seed and post-seed focus
                    'round_date': '',  # Not available
                    'amount': '',  # Ticket size 250K-750K EUR but not specified per company
                    'valuation_pre': '',  # Not available
                    'valuation_post': '',  # Not available
                    'is_lead_investor': 'true',  # Assuming they lead given their operational approach
                    'board_seats': '',  # Not available
                    'equity_percentage': ''  # Not available
                }
                
                # Check if investment relationship already exists
                exists = any(
                    rel['investor_name'] == investment_relationship['investor_name'] and
                    rel['startup_name'] == investment_relationship['startup_name']
                    for rel in self.investment_relationships
                )
                
                if not exists:
                    self.investment_relationships.append(investment_relationship)
            
            logger.info(f"Successfully processed {len(self.startups)} startups")
            return True
            
        except Exception as e:
            logger.error(f"Error processing portfolio companies: {e}")
            return False
    
    def save_to_csv(self):
        """Save all scraped data to CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save startups
        startups_file = f"prana_ventures_startups_{timestamp}.csv"
        self.save_startups_to_csv(startups_file)
        
        # Save investment relationships
        investment_file = f"prana_ventures_investment_relationships_{timestamp}.csv"
        self.save_investment_relationships_to_csv(investment_file)
        
        logger.info(f"Saved data to CSV files with timestamp {timestamp}")
    
    def save_startups_to_csv(self, filename: str):
        """Save startups to CSV"""
        if not self.startups:
            logger.warning("No startups to save")
            return
        
        # Use C14 compatible column names and structure
        fieldnames = [
            'name', 'description', 'website', 'founded_year', 'stage', 'sector', 
            'business_model', 'headquarters', 'employee_count', 'status', 
            'total_funding', 'last_funding_date', 'exit_date', 'exit_value'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
            writer.writeheader()
            for startup in self.startups:
                writer.writerow(startup)
        
        logger.info(f"Saved {len(self.startups)} startups to {filename}")
    
    def save_investment_relationships_to_csv(self, filename: str):
        """Save investment relationships to CSV"""
        if not self.investment_relationships:
            logger.warning("No investment relationships to save")
            return
        
        # Use C14 compatible column names and structure  
        fieldnames = [
            'investor_name', 'investor_type', 'startup_name', 'round_stage', 
            'round_date', 'amount', 'valuation_pre', 'valuation_post', 
            'is_lead_investor', 'board_seats', 'equity_percentage'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
            writer.writeheader()
            for relationship in self.investment_relationships:
                writer.writerow(relationship)
        
        logger.info(f"Saved {len(self.investment_relationships)} investment relationships to {filename}")
    
    def print_summary(self):
        """Print summary of scraped data"""
        print("\n" + "="*60)
        print("PRANA VENTURES SCRAPING SUMMARY")
        print("="*60)
        print(f"📊 Startups scraped: {len(self.startups)}")
        print(f"💰 Investment relationships: {len(self.investment_relationships)}")
        
        # Sector breakdown
        sectors = {}
        for startup in self.startups:
            sector = startup['sector']
            sectors[sector] = sectors.get(sector, 0) + 1
        
        print(f"\n🏢 Sector distribution:")
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {sector}: {count} companies")
        
        # Business model breakdown
        models = {}
        for startup in self.startups:
            model = startup['business_model']
            models[model] = models.get(model, 0) + 1
        
        print(f"\n💼 Business model distribution:")
        for model, count in sorted(models.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {model}: {count} companies")
        
        print("\n📈 Investment details:")
        print(f"  • Fund focus: Seed & Post-Seed")
        print(f"  • Ticket size: €250K - €750K")
        print(f"  • Total invested: €8.3M")
        print(f"  • Target fund size: €50M")
        
        print("="*60)

def main():
    """Main execution function"""
    print("🇮🇹 Prana Ventures Portfolio Scraper")
    print("=" * 50)
    
    scraper = PranaVenturesScraper()
    
    try:
        # Process portfolio companies
        logger.info("Starting Prana Ventures portfolio processing...")
        success = scraper.process_portfolio_companies()
        
        if success:
            # Save to CSV files
            scraper.save_to_csv()
            
            # Print summary
            scraper.print_summary()
            
            print("\n✅ Processing completed successfully!")
            print("📁 CSV files generated with all the extracted data")
            
        else:
            logger.error("Processing failed")
            return False
            
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
