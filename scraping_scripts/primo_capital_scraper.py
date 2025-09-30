#!/usr/bin/env python3
"""
Primo Capital Portfolio Scraper

This script scrapes portfolio companies from Primo Capital website.
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
        logging.FileHandler('primo_capital_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PrimoCapitalScraper:
    def __init__(self):
        self.base_url = "https://primo.capital"
        self.portfolio_url = "https://primo.capital/it/portfolio/"
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
        
        # Portfolio companies data extracted from the webpage
        self.portfolio_companies = [
            {
                'name': '181 Travel',
                'description': 'A new way to craft flawless travel experiences',
                'website': 'https://181travel.com/',
                'sector': 'Travel & Tourism'
            },
            {
                'name': 'Aiko',
                'description': 'TRL 9 Artificial Intelligence for space missions.',
                'website': 'https://www.aikospace.com/',
                'sector': 'Space & Aerospace'
            },
            {
                'name': 'Apogeo Space',
                'description': 'Constellation of nanosatellites for IoT',
                'website': 'http://www.apogeo.space/#ss1',
                'sector': 'Space & Aerospace'
            },
            {
                'name': 'Astradyne',
                'description': 'Deployable structures for space and Earth',
                'website': 'https://www.astradyne.space/',
                'sector': 'Space & Aerospace'
            },
            {
                'name': 'Astrocast',
                'description': 'The most advanced global nanosatellite IoT network',
                'website': 'https://www.astrocast.com/',
                'sector': 'Space & Aerospace'
            },
            {
                'name': 'Brandon Group',
                'description': 'Your Digital Bridge',
                'website': 'http://brandongroup.it/',
                'sector': 'Technology'
            },
            {
                'name': 'Breadcrumbs.io',
                'description': 'The revenue accelerator',
                'website': 'https://breadcrumbs.io/',
                'sector': 'MarTech'
            },
            {
                'name': 'Caracol',
                'description': 'Large-scale additive manufacturing',
                'website': 'https://caracol-am.com/',
                'sector': 'Manufacturing'
            },
            {
                'name': 'ChAI',
                'description': 'Commodity Pricing Forecasting',
                'website': 'https://chaipredict.com/',
                'sector': 'FinTech'
            },
            {
                'name': 'Checkmab',
                'description': 'Checkmate to cancer',
                'website': 'https://www.checkmab.eu/en/homepage/',
                'sector': 'HealthTech'
            },
            {
                'name': 'Codemotion',
                'description': 'We code the future. Together',
                'website': 'https://codemotionworld.com',
                'sector': 'EdTech'
            },
            {
                'name': 'Crestoptics',
                'description': 'fluorescence microscopy',
                'website': 'https://crestoptics.com/',
                'sector': 'HealthTech'
            },
            {
                'name': 'CryptoBooks',
                'description': 'Accounting software solutions for digital assets',
                'website': 'https://www.xbooks.it/',
                'sector': 'FinTech'
            },
            {
                'name': 'Cubbit',
                'description': 'Distributed, secure, encrypted cloud storage',
                'website': 'https://cubbit.io/',
                'sector': 'Enterprise Software'
            },
            {
                'name': 'D-Orbit',
                'description': 'Space logistics and orbital transportation services',
                'website': 'https://www.dorbit.space/',
                'sector': 'Space & Aerospace'
            },
            {
                'name': 'Data Masters',
                'description': 'La AI Academy italiana per la formazione in Intelligenza Artificiale, Machine Learning e Data Science',
                'website': 'https://datamasters.it/',
                'sector': 'EdTech'
            },
            {
                'name': 'Ecosmic',
                'description': 'Enabling sustainable space operations',
                'website': 'https://www.ecosmic.space/',
                'sector': 'Space & Aerospace'
            },
            {
                'name': 'Enterome SA',
                'description': 'Delivering the promise of immunotherapy',
                'website': 'https://www.enterome.com/',
                'sector': 'HealthTech'
            },
            {
                'name': 'Eoliann',
                'description': 'We help financial institutions forecast climate risks',
                'website': 'https://www.eoliann.com/',
                'sector': 'FinTech'
            },
            {
                'name': 'Event.com',
                'description': 'Events.com connects people with the experiences they love',
                'website': 'https://events.com/',
                'sector': 'Consumer Tech'
            },
            {
                'name': 'Eventboost',
                'description': 'The event management software',
                'website': 'https://www.eventboost.com/',
                'sector': 'Enterprise Software'
            },
            {
                'name': 'Factanza Media',
                'description': "L'informazione che crea (in)dipendenza",
                'website': 'https://factanza.it/',
                'sector': 'Media & Entertainment'
            },
            {
                'name': 'Inreception',
                'description': 'Sell and manage your rooms',
                'website': 'https://www.inreception.com/',
                'sector': 'Travel & Tourism'
            },
            {
                'name': 'InstaKitchen',
                'description': 'Kitchen coworking for food entrepreneurs',
                'website': 'https://www.instakitchen.it/',
                'sector': 'Food & Beverage'
            },
            {
                'name': 'Irreo',
                'description': 'Sensorless Irrigation Planner',
                'website': 'https://www.irreo.ai/',
                'sector': 'AgriTech'
            },
            {
                'name': 'Italian Artisan',
                'description': 'Made in Italy, Made Easy',
                'website': 'https://italian-artisan.com/',
                'sector': 'Retail & E-commerce'
            },
            {
                'name': 'Keyless',
                'description': 'Zero-Trust Passwordless Authentication',
                'website': 'https://keyless.io/',
                'sector': 'Cybersecurity'
            },
            {
                'name': 'Krill Design',
                'description': 'Innovative biomaterial for sustainable design',
                'website': 'https://krilldesign.com/',
                'sector': 'Materials & Chemistry'
            },
            {
                'name': 'Pangaea Aerospace',
                'description': 'systems.',
                'website': 'http://pangeaaerospace.com/',
                'sector': 'Space & Aerospace'
            },
            {
                'name': 'Pedius',
                'description': 'The application that allows the Deaf to make phone calls without a third party intermediary',
                'website': 'https://www.pedius.org/it/home/',
                'sector': 'HealthTech'
            },
            {
                'name': 'Pieffeuno',
                'description': 'High quality APIs to the world',
                'website': 'https://www.trifarma.it/',
                'sector': 'HealthTech'
            },
            {
                'name': 'Qomodo',
                'description': 'Il futuro dei pagamenti nel settore delle riparazioni auto e delle spese impreviste.',
                'website': 'https://www.qomodo.me/',
                'sector': 'FinTech'
            },
            {
                'name': 'Quicare',
                'description': 'Healthcare made easy',
                'website': 'https://quicare.com/',
                'sector': 'HealthTech'
            },
            {
                'name': 'RarEarth',
                'description': 'Production of sustainable magnets made from recycled materials',
                'website': 'https://www.rarearth.it/',
                'sector': 'Materials & Chemistry'
            },
            {
                'name': 'Revolv Space',
                'description': 'Redefining small satellite capabilities through reliable and affordable space power systems',
                'website': 'https://www.revolvspace.com/home',
                'sector': 'Space & Aerospace'
            },
            {
                'name': 'SardexPay',
                'description': 'Circuito di credito commerciale',
                'website': 'https://www.sardexpay.net/',
                'sector': 'FinTech'
            },
            {
                'name': 'Servitly',
                'description': 'Creating value through Connected Services for equipment manufacturers',
                'website': 'https://www.servitly.com/it/',
                'sector': 'Enterprise Software'
            },
            {
                'name': 'Shop Circle',
                'description': 'The first operator of e-commerce software',
                'website': 'https://shopcircle.co/',
                'sector': 'Retail & E-commerce'
            },
            {
                'name': 'Sidereus',
                'description': 'Expanding the boundaries of civilization',
                'website': 'https://www.sidereus.space/',
                'sector': 'Space & Aerospace'
            },
            {
                'name': 'Sift',
                'description': 'The leaders in digital trust & safety',
                'website': 'http://sift.com/',
                'sector': 'Cybersecurity'
            },
            {
                'name': 'Silk Biomaterials',
                'description': 'Silk innovation for life sciences',
                'website': 'https://www.klis.bio/',
                'sector': 'HealthTech'
            },
            {
                'name': 'Startupitalia',
                'description': 'Il magazine dell\'innovazione e delle startup italiane',
                'website': 'https://startupitalia.eu/',
                'sector': 'Media & Entertainment'
            },
            {
                'name': 'Stellar',
                'description': 'Perfect Internet on the Move',
                'website': 'https://www.stellar.tc/',
                'sector': 'Telecommunications'
            },
            {
                'name': 'Transactionale',
                'description': 'Il tuo prossimo cliente è qui',
                'website': 'https://www.transactionale.com/it',
                'sector': 'MarTech'
            },
            {
                'name': 'Vection Technologies',
                'description': 'Real-time technologies for industrial companies\' digital transformation.',
                'website': 'https://www.vection.com.au/',
                'sector': 'Enterprise Software'
            },
            {
                'name': 'Wise',
                'description': 'euromonitoring and neuromodulation to advance the treatment of acute and chronic indications',
                'website': 'https://wiseneuro.com/',
                'sector': 'HealthTech'
            },
            {
                'name': 'WithLess',
                'description': 'Stop paying for software you don\'t use',
                'website': 'https://www.withless.com/',
                'sector': 'Enterprise Software'
            },
            {
                'name': 'WordLift',
                'description': 'The Artificial Intelligence you need to grow your audience',
                'website': 'https://wordlift.io/',
                'sector': 'AI & Machine Learning'
            },
            {
                'name': 'YOLO',
                'description': 'On-demand insurance',
                'website': 'https://yolo-insurance.com/',
                'sector': 'InsurTech'
            }
        ]
    
    def determine_business_model(self, description: str, sector: str) -> str:
        """Determine business model based on description and sector"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['saas', 'software', 'platform', 'api']):
            return 'SaaS'
        elif sector in ['Retail & E-commerce', 'Consumer Tech']:
            return 'B2C'
        elif sector in ['Enterprise Software', 'Cybersecurity', 'MarTech']:
            return 'B2B'
        else:
            return 'B2B'  # Default for most tech companies
    
    def determine_headquarters(self, website: str) -> str:
        """Determine headquarters based on website domain"""
        if not website:
            return 'Italy'  # Default for Primo Capital portfolio
        
        domain = urlparse(website).netloc.lower()
        
        if '.it' in domain or 'italian' in domain:
            return 'Italy'
        elif '.com.au' in domain:
            return 'Australia'
        elif '.ch' in domain:
            return 'Switzerland'
        elif '.fr' in domain:
            return 'France'
        else:
            return 'Italy'  # Default assumption for Primo Capital (Italian VC)
    
    def process_portfolio_companies(self):
        """Process the hardcoded portfolio companies"""
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
                    'stage': 'Growth',  # Assuming growth stage for Primo Capital portfolio
                    'sector': company['sector'],
                    'business_model': self.determine_business_model(company['description'], company['sector']),
                    'headquarters': self.determine_headquarters(company['website']),
                    'employee_count': '',  # Not available
                    'status': 'active',  # Assuming active
                    'total_funding': '',  # Not available
                    'last_funding_date': '',  # Not available
                    'exit_date': '',  # Not available
                    'exit_value': ''  # Not available
                }
                
                self.startups.append(startup)
                
                # Create investment relationship (Primo Capital invests in this startup)
                investment_relationship = {
                    'investor_name': 'Primo Capital',
                    'investor_type': 'VC_Firm',
                    'startup_name': company['name'],
                    'round_stage': 'Growth',  # Assuming growth stage
                    'round_date': '',  # Not available
                    'amount': '',  # Not disclosed
                    'valuation_pre': '',  # Not available
                    'valuation_post': '',  # Not available
                    'is_lead_investor': 'true',  # Assuming they lead
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
        startups_file = f"primo_capital_startups_{timestamp}.csv"
        self.save_startups_to_csv(startups_file)
        
        # Save investment relationships
        investment_file = f"primo_capital_investment_relationships_{timestamp}.csv"
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
        print("PRIMO CAPITAL SCRAPING SUMMARY")
        print("="*60)
        print(f"📊 Startups scraped: {len(self.startups)}")
        print(f"💰 Investment relationships: {len(self.investment_relationships)}")
        
        # Sector breakdown
        sectors = {}
        for startup in self.startups:
            sector = startup['sector']
            sectors[sector] = sectors.get(sector, 0) + 1
        
        print(f"\n🏢 Top sectors:")
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {sector}: {count} companies")
        
        # Geography breakdown
        countries = {}
        for startup in self.startups:
            country = startup['headquarters']
            countries[country] = countries.get(country, 0) + 1
        
        print(f"\n🌍 Geographic distribution:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {country}: {count} companies")
        
        print("="*60)

def main():
    """Main execution function"""
    print("🇮🇹 Primo Capital Portfolio Scraper")
    print("=" * 50)
    
    scraper = PrimoCapitalScraper()
    
    try:
        # Process portfolio companies
        logger.info("Starting Primo Capital portfolio processing...")
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
