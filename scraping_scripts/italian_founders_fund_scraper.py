#!/usr/bin/env python3
"""
Italian Founders Fund Portfolio Scraper

This script scrapes portfolio companies and their founders from Italian Founders Fund website.
Extracts startup information, founder details, and generates CSV files for our knowledge graph.
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
        logging.FileHandler('italian_founders_fund_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ItalianFoundersFundScraper:
    def __init__(self):
        self.base_url = "https://www.italianfoundersfund.com"
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
        self.founders = []
        self.investment_relationships = []
        self.founding_relationships = []
        
        # Country mapping based on flag icons
        self.country_mapping = {
            'icons8-italy-96.png': 'Italy',
            'icons8-usa-96.png': 'United States',
            'icons8-uk-96.png': 'United Kingdom',
            'icons8-singapore-96.png': 'Singapore'
        }
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Add delay to be respectful
            time.sleep(1)
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        # Remove HTML entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        return text.strip()
    
    def extract_country_from_flag(self, soup) -> str:
        """Extract country from flag icon"""
        try:
            flag_img = soup.find('img', class_='image-5')
            if flag_img and flag_img.get('src'):
                src = flag_img.get('src')
                for flag_file, country in self.country_mapping.items():
                    if flag_file in src:
                        return country
            return 'Unknown'
        except:
            return 'Unknown'
    
    def parse_founder_name(self, full_name: str) -> Tuple[str, str]:
        """Parse full name into first name and last name"""
        if not full_name:
            return "", ""
        
        name_parts = full_name.strip().split()
        if len(name_parts) == 1:
            return name_parts[0], ""
        elif len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
            return first_name, last_name
        
        return full_name, ""
    
    def extract_linkedin_username(self, linkedin_url: str) -> str:
        """Extract LinkedIn username from URL"""
        if not linkedin_url:
            return ""
        
        # Clean up common LinkedIn URL patterns
        linkedin_url = linkedin_url.replace('https://www.linkedin.com/in/', '')
        linkedin_url = linkedin_url.replace('http://www.linkedin.com/in/', '')
        linkedin_url = linkedin_url.rstrip('/')
        
        # Handle duplicate URLs in the HTML (like the Simone Patera case)
        if 'https://www.linkedin.com/in/' in linkedin_url:
            linkedin_url = linkedin_url.split('https://www.linkedin.com/in/')[-1]
        
        # Remove query parameters and trailing slashes
        linkedin_url = linkedin_url.split('?')[0].rstrip('/')
        
        return linkedin_url
    
    def scrape_portfolio(self) -> bool:
        """Scrape portfolio companies from Italian Founders Fund"""
        try:
            # Fetch the main page
            soup = self.fetch_page(self.base_url)
            if not soup:
                logger.error("Failed to fetch main page")
                return False
            
            # Find all portfolio cards
            portfolio_cards = soup.find_all('div', class_='card-portfolio')
            logger.info(f"Found {len(portfolio_cards)} portfolio companies")
            
            for i, card in enumerate(portfolio_cards, 1):
                try:
                    logger.info(f"Processing startup {i}/{len(portfolio_cards)}")
                    self.process_portfolio_card(card)
                except Exception as e:
                    logger.error(f"Error processing portfolio card {i}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(self.startups)} startups")
            return True
            
        except Exception as e:
            logger.error(f"Error in scrape_portfolio: {e}")
            return False
    
    def process_portfolio_card(self, card):
        """Process individual portfolio card"""
        try:
            # Find the popup with detailed information
            popup = card.find('div', class_='pop-up-portfolio')
            if not popup:
                logger.warning("No popup found for portfolio card")
                return
            
            # Extract startup basic info
            startup_name = ""
            h3_element = popup.find('h3')
            if h3_element:
                startup_name = self.clean_text(h3_element.get_text())
            
            if not startup_name:
                logger.warning("No startup name found")
                return
            
            # Extract description
            description = ""
            desc_element = popup.find('p', class_='portfolio_text')
            if desc_element:
                description = self.clean_text(desc_element.get_text())
            
            # Extract website
            website = ""
            website_link = popup.find('a', class_='button-block-34')
            if website_link and website_link.get('href'):
                website = website_link.get('href')
            
            # Extract country from flag
            country = self.extract_country_from_flag(popup)
            
            # Determine sector based on description keywords
            sector = self.determine_sector(description)
            
            # Create startup record with C14 compatible structure
            startup = {
                'name': startup_name,
                'description': description,
                'website': website,
                'founded_year': '',  # Not available in the HTML (renamed from founding_year)
                'stage': 'Seed',  # Assuming seed stage for IFF portfolio
                'sector': sector,
                'business_model': 'SaaS' if 'saas' in description.lower() else 'B2B',  # Simple heuristic
                'headquarters': country,  # Using country as headquarters
                'employee_count': '',  # Not available
                'status': 'active',  # Use lowercase to match C14 format
                'total_funding': '',  # Not available from IFF
                'last_funding_date': '',  # Not available from IFF
                'exit_date': '',  # Not available from IFF
                'exit_value': ''  # Not available from IFF
            }
            
            self.startups.append(startup)
            
            # Process founders
            self.process_founders(popup, startup_name)
            
        except Exception as e:
            logger.error(f"Error processing portfolio card: {e}")
    
    def extract_logo_url(self, card) -> str:
        """Extract logo URL from card"""
        try:
            img_element = card.find('img', class_='image-4')
            if img_element and img_element.get('src'):
                return img_element.get('src')
            
            # Fallback to popup image
            popup = card.find('div', class_='pop-up-portfolio')
            if popup:
                img_element = popup.find('img', class_='image-2')
                if img_element and img_element.get('src'):
                    return img_element.get('src')
            
            return ""
        except:
            return ""
    
    def determine_sector(self, description: str) -> str:
        """Determine sector based on description keywords"""
        if not description:
            return "Technology"
        
        desc_lower = description.lower()
        
        # Define sector keywords
        sector_keywords = {
            'FinTech': ['payment', 'finance', 'financial', 'fintech', 'banking', 'revenue'],
            'HealthTech': ['health', 'medical', 'healthcare', 'biotech', 'wellness', 'clinical'],
            'EdTech': ['education', 'learning', 'tutoring', 'educational', 'teaching'],
            'HR Tech': ['hr', 'human resources', 'recruitment', 'payroll', 'talent', 'skills'],
            'MarTech': ['marketing', 'advertising', 'market research', 'customer insights', 'ad spend'],
            'Energy & CleanTech': ['energy', 'sustainability', 'environmental', 'esg', 'clean'],
            'AI & Machine Learning': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'automation'],
            'IoT & Hardware': ['iot', 'internet of things', 'hardware', 'sensors', 'monitoring'],
            'Enterprise Software': ['enterprise', 'b2b', 'business', 'saas', 'software', 'platform'],
            'Consumer Tech': ['consumer', 'mobile', 'app', 'social', 'networking'],
            'Transportation': ['mobility', 'transportation', 'automotive', 'logistics'],
            'Real Estate': ['real estate', 'property', 'construction', 'housing'],
            'Retail & E-commerce': ['retail', 'e-commerce', 'ecommerce', 'shopping', 'marketplace']
        }
        
        # Check for sector matches
        for sector, keywords in sector_keywords.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    return sector
        
        return "Technology"  # Default
    
    def process_founders(self, popup, startup_name: str):
        """Process founders from popup"""
        try:
            founders_section = popup.find('div', class_='founders')
            if not founders_section:
                logger.warning(f"No founders section found for {startup_name}")
                return
            
            founder_items = founders_section.find_all('div', class_='founder-item')
            
            for founder_item in founder_items:
                try:
                    # Extract founder name from the link
                    founder_link = founder_item.find('a', class_='button-block-34')
                    founder_name = ""
                    linkedin_url = ""
                    
                    if founder_link:
                        # Get name from the job-title div
                        name_element = founder_link.find('div', class_='job-title')
                        if name_element:
                            founder_name = self.clean_text(name_element.get_text())
                        
                        # Get LinkedIn URL
                        linkedin_url = founder_link.get('href', '')
                    
                    if not founder_name:
                        logger.warning(f"No founder name found for {startup_name}")
                        continue
                    
                    # Parse name into first and last name
                    first_name, last_name = self.parse_founder_name(founder_name)
                    
                    # Clean LinkedIn URL
                    linkedin_username = self.extract_linkedin_username(linkedin_url)
                    
                    # Check if founder already exists (to avoid duplicates)
                    existing_founder = None
                    for founder in self.founders:
                        if (founder['name'] == first_name and 
                            founder['surname'] == last_name):
                            existing_founder = founder
                            break
                    
                    if not existing_founder:
                        # Create new founder
                        founder = {
                            'name': first_name,
                            'surname': last_name,
                            'role_type': 'Founder',
                            'linkedin_url': linkedin_url,
                            'twitter_handle': '',
                            'location': '',
                            'biography': '',
                            'birth_year': '',
                            'education': '',
                            'previous_experience': '',
                            'specialization': ''
                        }
                        self.founders.append(founder)
                    
                    # Create founding relationship
                    founding_relationship = {
                        'person_name': first_name,
                        'person_surname': last_name,
                        'startup_name': startup_name,
                        'role': 'Founder',
                        'founding_date': '',  # Not available
                        'equity_percentage': '',
                        'is_current': 'true',
                        'exit_date': ''
                    }
                    self.founding_relationships.append(founding_relationship)
                    
                    # Create investment relationship (IFF invests in this startup) with C14 compatible structure
                    investment_relationship = {
                        'investor_name': 'Italian Founders Fund',
                        'investor_type': 'VC_Firm',
                        'startup_name': startup_name,
                        'round_stage': 'Seed',  # Renamed from round_type
                        'round_date': '',  # Renamed from investment_date
                        'amount': '',  # Not disclosed
                        'valuation_pre': '',  # Not available from IFF
                        'valuation_post': '',  # Not available from IFF  
                        'is_lead_investor': 'true',  # Renamed from lead_investor, assuming they lead
                        'board_seats': '',  # Not available from IFF
                        'equity_percentage': ''  # Not available from IFF
                    }
                    
                    # Check if investment relationship already exists
                    exists = any(
                        rel['investor_name'] == investment_relationship['investor_name'] and
                        rel['startup_name'] == investment_relationship['startup_name']
                        for rel in self.investment_relationships
                    )
                    
                    if not exists:
                        self.investment_relationships.append(investment_relationship)
                    
                except Exception as e:
                    logger.error(f"Error processing founder for {startup_name}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error processing founders for {startup_name}: {e}")
    
    def save_to_csv(self):
        """Save all scraped data to CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save startups
        startups_file = f"iff_startups_{timestamp}.csv"
        self.save_startups_to_csv(startups_file)
        
        # Save founders  
        founders_file = f"iff_founders_{timestamp}.csv"
        self.save_founders_to_csv(founders_file)
        
        # Save founding relationships
        founding_file = f"iff_founding_relationships_{timestamp}.csv"
        self.save_founding_relationships_to_csv(founding_file)
        
        # Save investment relationships
        investment_file = f"iff_investment_relationships_{timestamp}.csv"
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
                # Map to C14 compatible format
                compatible_startup = {
                    'name': startup.get('name', ''),
                    'description': startup.get('description', ''),
                    'website': startup.get('website', ''),
                    'founded_year': startup.get('founding_year', ''),  # Map founding_year to founded_year
                    'stage': startup.get('stage', ''),
                    'sector': startup.get('sector', ''),
                    'business_model': startup.get('business_model', ''),
                    'headquarters': startup.get('headquarters', ''),
                    'employee_count': startup.get('employee_count', ''),
                    'status': startup.get('status', ''),
                    'total_funding': '',  # Not available from IFF
                    'last_funding_date': '',  # Not available from IFF
                    'exit_date': '',  # Not available from IFF
                    'exit_value': ''  # Not available from IFF
                }
                writer.writerow(compatible_startup)
        
        logger.info(f"Saved {len(self.startups)} startups to {filename}")
    
    def save_founders_to_csv(self, filename: str):
        """Save founders to CSV"""
        if not self.founders:
            logger.warning("No founders to save")
            return
        
        # Use C14 compatible column names and structure
        fieldnames = [
            'name', 'surname', 'role_type', 'linkedin_url', 'twitter_handle',
            'location', 'biography', 'birth_year', 'education', 'previous_experience', 'specialization', 'reputation_score'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
            writer.writeheader()
            for founder in self.founders:
                # Add reputation_score field for C14 compatibility
                founder_with_score = founder.copy()
                founder_with_score['reputation_score'] = ''  # Not available from IFF
                writer.writerow(founder_with_score)
        
        logger.info(f"Saved {len(self.founders)} founders to {filename}")
    
    def save_founding_relationships_to_csv(self, filename: str):
        """Save founding relationships to CSV"""
        if not self.founding_relationships:
            logger.warning("No founding relationships to save")
            return
        
        fieldnames = [
            'person_name', 'person_surname', 'startup_name', 'role',
            'founding_date', 'equity_percentage', 'is_current', 'exit_date'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
            writer.writeheader()
            for relationship in self.founding_relationships:
                writer.writerow(relationship)
        
        logger.info(f"Saved {len(self.founding_relationships)} founding relationships to {filename}")
    
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
                # Map to C14 compatible format
                compatible_relationship = {
                    'investor_name': relationship.get('investor_name', ''),
                    'investor_type': relationship.get('investor_type', ''),
                    'startup_name': relationship.get('startup_name', ''),
                    'round_stage': relationship.get('round_type', ''),  # Map round_type to round_stage
                    'round_date': relationship.get('investment_date', ''),  # Map investment_date to round_date
                    'amount': relationship.get('amount', ''),
                    'valuation_pre': '',  # Not available from IFF
                    'valuation_post': '',  # Not available from IFF
                    'is_lead_investor': relationship.get('lead_investor', ''),  # Map lead_investor to is_lead_investor
                    'board_seats': '',  # Not available from IFF
                    'equity_percentage': ''  # Not available from IFF
                }
                writer.writerow(compatible_relationship)
        
        logger.info(f"Saved {len(self.investment_relationships)} investment relationships to {filename}")
    
    def print_summary(self):
        """Print summary of scraped data"""
        print("\n" + "="*60)
        print("ITALIAN FOUNDERS FUND SCRAPING SUMMARY")
        print("="*60)
        print(f"📊 Startups scraped: {len(self.startups)}")
        print(f"👥 Founders extracted: {len(self.founders)}")
        print(f"🤝 Founding relationships: {len(self.founding_relationships)}")
        print(f"💰 Investment relationships: {len(self.investment_relationships)}")
        
        if self.startups:
            print(f"\n🏢 Sample startups:")
            for startup in self.startups[:5]:
                print(f"  • {startup['name']} ({startup['sector']}) - {startup['headquarters']}")
        
        if self.founders:
            print(f"\n👤 Sample founders:")
            for founder in self.founders[:5]:
                print(f"  • {founder['name']} {founder['surname']}")
        
        print("="*60)

def main():
    """Main execution function"""
    print("🇮🇹 Italian Founders Fund Portfolio Scraper")
    print("=" * 50)
    
    scraper = ItalianFoundersFundScraper()
    
    try:
        # Scrape portfolio
        logger.info("Starting Italian Founders Fund portfolio scraping...")
        success = scraper.scrape_portfolio()
        
        if success:
            # Save to CSV files
            scraper.save_to_csv()
            
            # Print summary
            scraper.print_summary()
            
            print("\n✅ Scraping completed successfully!")
            print("📁 CSV files generated with all the extracted data")
            
        else:
            logger.error("Scraping failed")
            return False
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
