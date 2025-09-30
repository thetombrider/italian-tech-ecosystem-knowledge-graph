#!/usr/bin/env python3
"""
CDP Venture Capital Portfolio Scraper
Scrapes portfolio data from CDP Venture Capital HTML file
"""

import os
import sys
import csv
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CDPVentureCapitalScraper:
    def __init__(self):
        self.startups = []
        self.vc_funds = []
        self.cdp_funds = []  # CDP's own funds
        self.investment_relationships = []
        self.fund_relationships = []
        self.investors = []
        
        # Path to HTML file
        self.html_file_path = os.path.join(os.path.dirname(__file__), '..', 'CDP.html')
        
        # Define sector mapping
        self.sector_mapping = {
            'Clean Tech': 'CleanTech',
            'Healthcare & Lifescience': 'HealthTech',
            'IndustryTech': 'IndustryTech',
            'InfraTech & Mobility': 'Mobility & Transportation',
            'AgriTech & FoodTech': 'AgriTech & FoodTech',
            'Other': 'Other',
            'tecnologiaAi': 'AI & Machine Learning'
        }
        
        # Region mapping to standard format
        self.region_mapping = {
            'Altro': 'Italy',
            'Lombardia': 'Italy',
            'Lazio': 'Italy',
            'Piemonte': 'Italy',
            'Campania': 'Italy',
            'Puglia': 'Italy',
            'Veneto': 'Italy',
            'Emilia-Romagna': 'Italy',
            'Toscana': 'Italy',
            'Sicilia': 'Italy',
            'Calabria': 'Italy',
            'Liguria': 'Italy',
            'Trentino-Alto Adige': 'Italy',
            'Friuli-Venezia Giulia': 'Italy',
            'Sardegna': 'Italy',
            'Basilicata': 'Italy',
            'Umbria': 'Italy',
            'Marche': 'Italy',
            'Abruzzo': 'Italy',
            'Molise': 'Italy',
            'Valle d\'Aosta': 'Italy'
        }
        
        # CDP's own funds
        self.cdp_fund_vehicles = {
            'VenturItaly Fund of Funds': {
                'name': 'VenturItaly Fund of Funds',
                'description': 'CDP Venture Capital fund-of-funds investing in Italian VC funds',
                'website': 'https://www.cdpventurecapital.it/en/fondi.page',
                'focus': 'Fund of Funds',
                'founded_year': '2019'
            },
            'VenturItaly II Fund of Funds': {
                'name': 'VenturItaly II Fund of Funds',
                'description': 'CDP Venture Capital second fund-of-funds investing in Italian VC funds',
                'website': 'https://www.cdpventurecapital.it/en/fondi.page',
                'focus': 'Fund of Funds',
                'founded_year': '2021'
            },
            'Technology Transfer Fund': {
                'name': 'Technology Transfer Fund',
                'description': 'CDP Venture Capital fund supporting technology transfer and innovation',
                'website': 'https://www.cdpventurecapital.it/en/fondi.page',
                'focus': 'Technology Transfer',
                'founded_year': '2020'
            },
            'International Fund of Funds': {
                'name': 'International Fund of Funds',
                'description': 'CDP Venture Capital fund-of-funds with international investment scope',
                'website': 'https://www.cdpventurecapital.it/en/fondi.page',
                'focus': 'International',
                'founded_year': '2020'
            },
            'Digital Transition NRRP Fund': {
                'name': 'Digital Transition NRRP Fund',
                'description': 'CDP Venture Capital NRRP fund for digital transformation',
                'website': 'https://www.cdpventurecapital.it/en/fondi.page',
                'focus': 'Digital Innovation',
                'founded_year': '2022'
            },
            'Green Transition NRRP Fund': {
                'name': 'Green Transition NRRP Fund',
                'description': 'CDP Venture Capital NRRP fund for green transition',
                'website': 'https://www.cdpventurecapital.it/en/fondi.page',
                'focus': 'Green Tech',
                'founded_year': '2022'
            }
        }
    
    def parse_html_file(self):
        """Parse the HTML file and extract portfolio data"""
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all portfolio cards
            portfolio_cards = soup.find_all('div', class_='blocks-portfolio__card-wrapper')
            logger.info(f"Found {len(portfolio_cards)} portfolio items")
            
            direct_investments = 0
            supported_funds = 0
            
            for card in portfolio_cards:
                category = card.get('data-category', '')
                
                if category == 'InvestimentoDiretto':
                    self.process_direct_investment(card)
                    direct_investments += 1
                elif category == 'FondiSupportati':
                    self.process_supported_fund(card)
                    supported_funds += 1
            
            logger.info(f"Processed {direct_investments} direct investments and {supported_funds} supported funds")
            
            # Create CDP funds records
            self.create_cdp_funds()
            
            # Create main CDP Venture Capital investor
            self.create_main_investor()
            
        except Exception as e:
            logger.error(f"Error parsing HTML file: {e}")
            raise
    
    def create_cdp_funds(self):
        """Create records for CDP's own funds"""
        for vehicle_key, fund_info in self.cdp_fund_vehicles.items():
            cdp_fund = {
                'name': fund_info['name'],
                'description': fund_info['description'],
                'website': fund_info['website'],
                'founded_year': fund_info['founded_year'],
                'headquarters': 'Italy',
                'type': 'VC_Fund',
                'investment_focus': fund_info['focus'],
                'stage_focus': 'Growth',
                'geographic_focus': 'Italy',
                'team_size': '',
                'assets_under_management': '',
                'portfolio_companies_count': ''
            }
            self.cdp_funds.append(cdp_fund)

    def extract_specific_funds_from_vehicle(self, vehicle):
        """Extract individual fund names from vehicle string"""
        funds = []
        if '/' in vehicle:
            # Multiple funds mentioned
            parts = vehicle.split('/')
            for part in parts:
                fund_name = part.strip()
                if fund_name in self.cdp_fund_vehicles:
                    funds.append(fund_name)
        else:
            # Single fund
            if vehicle in self.cdp_fund_vehicles:
                funds.append(vehicle)
        
        return funds if funds else [vehicle]  # Return original if no match

    def process_direct_investment(self, card):
        """Process a direct investment (startup where CDP invested directly)"""
        try:
            # Extract company name
            name_element = card.find('h4', class_='h4')
            if not name_element:
                return
            
            company_name = name_element.get_text(strip=True)
            
            # Extract website
            website_link = card.find('a', class_='btn-animated-icon-grey')
            website = website_link.get('href', '') if website_link else ''
            
            # Extract vehicle info (which CDP fund made the investment)
            vehicle = card.get('data-veicolo', '').strip()
            
            # Extract sector from data-settore attribute
            raw_sector = card.get('data-settore', '').strip()
            sector = self.map_sector(raw_sector)
            
            # Extract region from data-regione attribute
            raw_region = card.get('data-regione', '').strip()
            headquarters = self.region_mapping.get(raw_region, 'Italy')
            
            # Determine business model based on sector
            business_model = self.determine_business_model(sector)
            
            # Create startup record
            startup = {
                'name': company_name,
                'description': f'{sector} company',
                'website': website,
                'founded_year': '',  # Not available in HTML
                'stage': 'Growth',  # CDP typically invests in later stages
                'sector': sector,
                'business_model': business_model,
                'headquarters': headquarters,
                'employee_count': '',  # Not available
                'status': 'active',  # Assuming active
                'total_funding': '',  # Not available
                'last_funding_date': '',  # Not available
                'exit_date': '',  # Not available
                'exit_value': ''  # Not available
            }
            
            self.startups.append(startup)
            
            # Create investment relationship(s)
            if vehicle:
                # Investment made by specific CDP fund
                specific_funds = self.extract_specific_funds_from_vehicle(vehicle)
                for fund_name in specific_funds:
                    investment_relationship = {
                        'investor_name': fund_name,
                        'investor_type': 'VC_Fund',
                        'startup_name': company_name,
                        'round_stage': 'Growth',
                        'round_date': '',
                        'amount': '',
                        'valuation_pre': '',
                        'valuation_post': '',
                        'is_lead_investor': 'true',
                        'board_seats': '',
                        'equity_percentage': ''
                    }
                    self.investment_relationships.append(investment_relationship)
            else:
                # Direct investment by CDP Venture Capital
                investment_relationship = {
                    'investor_name': 'CDP Venture Capital',
                    'investor_type': 'Government_VC',
                    'startup_name': company_name,
                    'round_stage': 'Growth',
                    'round_date': '',
                    'amount': '',
                    'valuation_pre': '',
                    'valuation_post': '',
                    'is_lead_investor': 'true',
                    'board_seats': '',
                    'equity_percentage': ''
                }
                self.investment_relationships.append(investment_relationship)
            
        except Exception as e:
            logger.error(f"Error processing direct investment: {e}")
    
    def process_supported_fund(self, card):
        """Process a supported fund (VC fund where CDP is LP)"""
        try:
            # Extract fund name
            name_element = card.find('h4', class_='h4')
            if not name_element:
                return
            
            fund_name = name_element.get_text(strip=True)
            
            # Extract website
            website_link = card.find('a', class_='btn-animated-icon-grey')
            website = website_link.get('href', '') if website_link else ''
            
            # Extract vehicle info (which CDP fund supports this)
            vehicle = card.get('data-veicolo', '')
            
            # Create VC fund record
            vc_fund = {
                'name': fund_name,
                'description': f'VC Fund supported by CDP Venture Capital through {vehicle}',
                'website': website,
                'founded_year': '',  # Not available
                'headquarters': 'Italy',  # Assuming Italy for CDP supported funds
                'type': 'VC_Fund',
                'investment_focus': 'Technology',
                'stage_focus': 'Growth',
                'geographic_focus': 'Italy',
                'team_size': '',  # Not available
                'assets_under_management': '',  # Not available
                'portfolio_companies_count': ''  # Not available
            }
            
            self.vc_funds.append(vc_fund)
            
            # Create fund relationship(s) with specific CDP funds
            if vehicle:
                specific_funds = self.extract_specific_funds_from_vehicle(vehicle)
                for cdp_fund_name in specific_funds:
                    fund_relationship = {
                        'investor_name': cdp_fund_name,
                        'investor_type': 'VC_Fund',
                        'fund_name': fund_name,
                        'commitment_amount': '',
                        'commitment_date': '',
                        'fund_vehicle': vehicle,
                        'relationship_type': 'LP',
                        'notes': f'{cdp_fund_name} acts as LP in {fund_name}',
                        'source': 'cdpventurecapital.it'
                    }
                    self.fund_relationships.append(fund_relationship)
            
        except Exception as e:
            logger.error(f"Error processing supported fund: {e}")
    
    def map_sector(self, raw_sector: str) -> str:
        """Map raw sector to our standard format"""
        # Handle multiple sectors (e.g., "Other , tecnologiaAi")
        sectors = [s.strip() for s in raw_sector.split(',')]
        
        for sector in sectors:
            if sector in self.sector_mapping:
                return self.sector_mapping[sector]
        
        # If no match found, try partial matching
        sector_lower = raw_sector.lower()
        if 'ai' in sector_lower or 'artificial' in sector_lower:
            return 'AI & Machine Learning'
        elif 'health' in sector_lower or 'medical' in sector_lower:
            return 'HealthTech'
        elif 'fintech' in sector_lower or 'finance' in sector_lower:
            return 'FinTech'
        elif 'clean' in sector_lower or 'green' in sector_lower:
            return 'CleanTech'
        else:
            return 'Other'
    
    def determine_business_model(self, sector: str) -> str:
        """Determine likely business model based on sector"""
        if sector in ['HealthTech', 'AI & Machine Learning', 'FinTech']:
            return 'SaaS'
        elif sector in ['CleanTech', 'IndustryTech']:
            return 'Hardware'
        elif sector in ['AgriTech & FoodTech']:
            return 'Marketplace'
        else:
            return 'Other'
    
    def create_main_investor(self):
        """Create the main CDP Venture Capital investor record"""
        investor = {
            'name': 'CDP Venture Capital',
            'description': 'Government venture capital arm of Cassa Depositi e Prestiti (CDP)',
            'website': 'https://www.cdpventurecapital.it',
            'founded_year': '2019',
            'headquarters': 'Italy',
            'type': 'Government_VC',
            'investment_focus': 'Technology, Innovation, Digital Transition, Green Tech',
            'stage_focus': 'Growth, Expansion',
            'geographic_focus': 'Italy, Europe',
            'team_size': '',
            'assets_under_management': '2000000000',  # €2B AUM
            'portfolio_companies_count': str(len(self.startups))
        }
        
        self.investors.append(investor)
    
    def save_to_csv(self):
        """Save all data to separate CSV files with descriptive names"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # ENTITIES - Save startups (portfolio companies)
        startups_file = f'cdp_entities_startup_portfolio_{timestamp}.csv'
        self.save_list_to_csv(self.startups, startups_file)
        logger.info(f"Saved {len(self.startups)} startup entities to {startups_file}")
        
        # ENTITIES - Save external VC funds supported by CDP
        external_funds_file = f'cdp_entities_vc_fund_external_{timestamp}.csv'
        self.save_list_to_csv(self.vc_funds, external_funds_file)
        logger.info(f"Saved {len(self.vc_funds)} external VC fund entities to {external_funds_file}")
        
        # ENTITIES - Save CDP's own funds
        cdp_funds_file = f'cdp_entities_vc_fund_internal_{timestamp}.csv'
        self.save_list_to_csv(self.cdp_funds, cdp_funds_file)
        logger.info(f"Saved {len(self.cdp_funds)} CDP internal fund entities to {cdp_funds_file}")
        
        # ENTITIES - Save main CDP investor entity
        main_investor_file = f'cdp_entities_vc_firm_main_{timestamp}.csv'
        self.save_list_to_csv(self.investors, main_investor_file)
        logger.info(f"Saved {len(self.investors)} main investor entity to {main_investor_file}")
        
        # RELATIONSHIPS - Save investment relationships (CDP funds → startups)
        investments_file = f'cdp_relationships_invests_in_{timestamp}.csv'
        self.save_list_to_csv(self.investment_relationships, investments_file)
        logger.info(f"Saved {len(self.investment_relationships)} INVESTS_IN relationships to {investments_file}")
        
        # RELATIONSHIPS - Save fund relationships (CDP funds → external funds as LP)
        fund_rels_file = f'cdp_relationships_participated_in_{timestamp}.csv'
        self.save_list_to_csv(self.fund_relationships, fund_rels_file)
        logger.info(f"Saved {len(self.fund_relationships)} PARTICIPATED_IN relationships to {fund_rels_file}")
    
    def save_list_to_csv(self, data_list, filename):
        """Save a list of dictionaries to a CSV file with pipe delimiter"""
        if not data_list:
            logger.warning(f"No data to save for {filename}")
            return
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data_list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
            writer.writeheader()
            writer.writerows(data_list)
    
    def run(self):
        """Main execution method"""
        logger.info("Starting CDP Venture Capital scraping...")
        
        # Check if HTML file exists
        if not os.path.exists(self.html_file_path):
            logger.error(f"HTML file not found: {self.html_file_path}")
            return
        
        # Parse HTML and extract data
        self.parse_html_file()
        
        # Save to CSV files
        self.save_to_csv()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print extraction summary with file naming guide"""
        logger.info("=== CDP VENTURE CAPITAL SCRAPING SUMMARY ===")
        logger.info("ENTITIES GENERATED:")
        logger.info(f"  📊 Startup entities: {len(self.startups)} (cdp_entities_startup_portfolio_*.csv)")
        logger.info(f"  🏦 External VC Fund entities: {len(self.vc_funds)} (cdp_entities_vc_fund_external_*.csv)")
        logger.info(f"  🏛️ CDP Fund entities: {len(self.cdp_funds)} (cdp_entities_vc_fund_internal_*.csv)")
        logger.info(f"  🏢 Main Investor entity: {len(self.investors)} (cdp_entities_vc_firm_main_*.csv)")
        logger.info("")
        logger.info("RELATIONSHIPS GENERATED:")
        logger.info(f"  💰 INVESTS_IN relationships: {len(self.investment_relationships)} (cdp_relationships_invests_in_*.csv)")
        logger.info(f"  🤝 PARTICIPATED_IN relationships: {len(self.fund_relationships)} (cdp_relationships_participated_in_*.csv)")
        logger.info("")
        logger.info("FILE NAMING CONVENTION:")
        logger.info("  • cdp_entities_[ENTITY_TYPE]_[SUBTYPE]_[TIMESTAMP].csv")
        logger.info("  • cdp_relationships_[RELATIONSHIP_TYPE]_[TIMESTAMP].csv")

if __name__ == "__main__":
    scraper = CDPVentureCapitalScraper()
    scraper.run()
