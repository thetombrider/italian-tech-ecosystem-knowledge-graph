"""
C14.so Scraper for Italian Tech Ecosystem Knowledge Graph
Scrapes startup data from C14.so database
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import logging
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs
import json
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class StartupData:
    """Data structure for startup information from C14"""
    name: str
    description: str
    website: str = ""
    linkedin: str = ""
    logo_url: str = ""
    location: str = ""
    foundation_date: str = ""
    team_size: str = ""
    funding_stage: str = ""
    amount_raised: str = ""
    sectors: List[str] = None
    team_members: List[Dict] = None
    investors: List[Dict] = None
    c14_url: str = ""
    uuid: str = ""

    def __post_init__(self):
        if self.sectors is None:
            self.sectors = []
        if self.team_members is None:
            self.team_members = []
        if self.investors is None:
            self.investors = []

@dataclass
class PersonData:
    name: str
    surname: str = ""
    role_type: str = ""
    linkedin_url: str = ""
    twitter_handle: str = ""
    biography: str = ""
    location: str = ""
    birth_year: Optional[int] = None
    education: str = ""
    previous_experience: str = ""
    specialization: str = ""
    reputation_score: Optional[float] = None

@dataclass
class InvestorData:
    name: str
    description: str = ""
    website: str = ""
    founded_year: Optional[int] = None
    headquarters: str = ""
    type: str = "VC_Firm"  # or Angel_Syndicate
    investment_focus: str = ""
    stage_focus: str = ""
    geographic_focus: str = ""
    team_size: Optional[int] = None
    assets_under_management: Optional[float] = None
    portfolio_companies_count: Optional[int] = None

def clean_url(url: str) -> str:
    """Remove UTM parameters and other tracking parameters from URL"""
    if not url:
        return url
    
    try:
        parsed = urlparse(url)
        # Parse query parameters
        query_params = parse_qs(parsed.query)
        
        # Remove UTM and tracking parameters
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
        for param in tracking_params:
            query_params.pop(param, None)
        
        # Rebuild query string
        if query_params:
            # Flatten the query params (parse_qs returns lists)
            clean_params = []
            for key, values in query_params.items():
                for value in values:
                    clean_params.append(f"{key}={value}")
            clean_query = "&".join(clean_params)
        else:
            clean_query = ""
        
        # Rebuild the URL
        clean_parsed = parsed._replace(query=clean_query)
        return urlunparse(clean_parsed)
    
    except Exception as e:
        logger.warning(f"Error cleaning URL {url}: {e}")
        return url

class C14Scraper:
    """Scraper for C14.so Italian startup database"""
    
    def __init__(self, delay: float = 1.0):
        self.base_url = "https://www.c14.so"
        self.delay = delay  # Rate limiting
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Collections for people and relationships
        self.all_founders = []
        self.all_investors = []
        self.founding_relationships = []
        self.investment_relationships = []
        
    def get_startup_links(self, max_pages: int = None) -> List[Tuple[str, str, str]]:
        """
        Get all startup links from C14.so startups page
        Returns list of tuples: (name, description, url)
        """
        startup_links = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
                
            url = f"{self.base_url}/startups"
            if page > 1:
                url += f"?page={page}"
                
            logger.info(f"Scraping page {page}: {url}")
            
            try:
                response = self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find startup links - they follow the pattern href="uuid"
                startup_elements = soup.find_all('a', href=re.compile(r'^[a-f0-9-]{36}$'))
                
                if not startup_elements:
                    logger.info(f"No more startups found on page {page}")
                    break
                
                for element in startup_elements:
                    try:
                        href = element.get('href')
                        if not href:
                            continue
                            
                        full_url = urljoin(self.base_url, href)
                        
                        # Extract name and description from the link text
                        text_content = element.get_text(strip=True)
                        if not text_content:
                            continue
                        
                        # Split name and description (usually "Name Description" format)
                        parts = text_content.split(' ', 1)
                        name = parts[0] if parts else ""
                        description = parts[1] if len(parts) > 1 else ""
                        
                        # Extract UUID from URL
                        uuid = href.split('/')[-1]
                        
                        startup_links.append((name, description, full_url, uuid))
                        
                    except Exception as e:
                        logger.warning(f"Error processing startup element: {e}")
                        continue
                
                logger.info(f"Found {len(startup_elements)} startups on page {page}")
                page += 1
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                break
        
        logger.info(f"Total startup links found: {len(startup_links)}")
        return startup_links
    
    def scrape_startup_details(self, url: str, uuid: str) -> Optional[StartupData]:
        """
        Scrape detailed information from a startup page
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info
            name = ""
            description = ""
            website = ""
            linkedin = ""
            logo_url = ""
            
            # Name (usually in h1)
            h1_element = soup.find('h1')
            if h1_element:
                name = h1_element.get_text(strip=True)
            
            # Logo
            img_element = soup.find('img', alt=name)
            if img_element:
                logo_url = img_element.get('src', '')
            
            # Description using the correct CSS selector
            desc_element = soup.select_one('.prose > p:nth-child(1)')
            if desc_element:
                description = desc_element.get_text(strip=True)
                # Remove line breaks and normalize whitespace
                description = ' '.join(description.split())
            else:
                # Fallback to previous method
                desc_candidates = soup.find_all(['p', 'div'], string=re.compile(r'.{20,}'))
                for candidate in desc_candidates:
                    text = candidate.get_text(strip=True)
                    # Remove line breaks and normalize whitespace
                    text = ' '.join(text.split())
                    if len(text) > 20 and not text.startswith('http'):
                        description = text
                        break
            
            # Links (website, linkedin)
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                if 'visit website' in text or 'website' in text:
                    website = clean_url(href)
                elif 'linkedin' in text or 'linkedin.com' in href:
                    linkedin = clean_url(href)
            
            # Company details using label-based approach for better reliability
            location = ""
            foundation_date = ""
            team_size = ""
            funding_stage = ""
            amount_raised = ""
            
            # Find all div.border-default elements
            border_divs = soup.select('div.border-default')
            
            for div in border_divs:
                # Look for divs with p elements that have labels
                child_divs = div.find_all('div', recursive=False)
                for child_div in child_divs:
                    p_elements = child_div.find_all('p', recursive=False)
                    if len(p_elements) >= 2:
                        label = p_elements[0].get_text(strip=True).lower()
                        value = p_elements[1].get_text(strip=True)
                        
                        if 'team size' in label:
                            team_size = value
                        elif 'location' in label:
                            location = value
                        elif 'foundation' in label:
                            foundation_date = value
                        elif 'funding stage' in label:
                            funding_stage = value
                        elif 'amount raised' in label:
                            amount_raised = value
            
            # Extract sectors using correct CSS selector
            sectors = []
            sector_element = soup.select_one('div.gap-1:nth-child(3)')
            if sector_element:
                # Get all sector tags within this element
                sector_tags = sector_element.find_all(['span', 'div'])
                for tag in sector_tags:
                    sector_text = tag.get_text(strip=True)
                    if sector_text and len(sector_text) < 50 and sector_text not in sectors:
                        sectors.append(sector_text)
            
            # Fallback to previous method if no sectors found
            if not sectors:
                sector_candidates = soup.find_all(['span', 'div', 'a'], class_=re.compile(r'tag|category|sector'))
                for candidate in sector_candidates:
                    sector_text = candidate.get_text(strip=True)
                    if sector_text and len(sector_text) < 50:
                        sectors.append(sector_text)
            
            # Extract founder team members using CSS selectors
            team_members = self.extract_founders(soup)
            
            # Extract investors using CSS selectors
            investors = self.extract_investors(soup)
            
            # Collect founders and relationships
            for founder in team_members:
                # Add to founders collection (avoid duplicates)
                if not any(f['name'] == founder['name'] for f in self.all_founders):
                    self.all_founders.append(founder)
                
                # Add founding relationship with separate name and surname
                full_name = founder['name'].strip()
                name_parts = full_name.split()
                person_name = name_parts[0] if name_parts else ""
                person_surname = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                self.founding_relationships.append({
                    'person_name': person_name,
                    'person_surname': person_surname,
                    'startup_name': name,
                    'role': founder['role'],
                    'founding_date': foundation_date,
                    'equity_percentage': '',
                    'is_current': 'true',
                    'exit_date': ''
                })
            
            # Collect investors and relationships
            for investor in investors:
                # Add to investors collection (avoid duplicates)
                if not any(inv['name'] == investor['name'] for inv in self.all_investors):
                    self.all_investors.append(investor)
                
                # Add investment relationship
                self.investment_relationships.append({
                    'investor_name': investor['name'],
                    'investor_type': investor['type'],
                    'startup_name': name,
                    'round_stage': funding_stage,
                    'round_date': '',
                    'amount': amount_raised,
                    'valuation_pre': '',
                    'valuation_post': '',
                    'is_lead_investor': '',
                    'board_seats': '',
                    'equity_percentage': ''
                })
            
            return StartupData(
                name=name,
                description=description,
                website=website,
                linkedin=linkedin,
                logo_url=logo_url,
                location=location,
                foundation_date=foundation_date,
                team_size=team_size,
                funding_stage=funding_stage,
                amount_raised=amount_raised,
                sectors=sectors,
                team_members=team_members,
                investors=investors,
                c14_url=url,
                uuid=uuid
            )
            
        except Exception as e:
            logger.error(f"Error scraping startup details from {url}: {e}")
            return None
    
    def extract_founders(self, soup) -> List[Dict]:
        """Extract founder information using CSS selectors"""
        founders = []
        
        try:
            # Use the specific founder section selector
            founder_container = soup.select_one('.mb-0 > div:nth-child(7) > div:nth-child(2) > div:nth-child(2)')
            
            if founder_container:
                # Find all LinkedIn links within the founder container only
                founder_links = founder_container.find_all('a', href=lambda href: href and 'linkedin.com' in href)
                
                for link in founder_links:
                    try:
                        linkedin_url = clean_url(link.get('href', ''))
                        
                        # Extract name from first p element within the link
                        name_element = link.select_one('div > div > p:nth-child(1)')
                        name = name_element.get_text(strip=True) if name_element else ""
                        
                        # Extract role from second p element within the link
                        role_element = link.select_one('div > div > p:nth-child(2)')
                        role = role_element.get_text(strip=True) if role_element else ""
                        
                        # Clean role to avoid CSV issues with pipe separator
                        role = role.replace('|', ' & ')  # Replace pipe with ampersand
                        
                        if name:
                            founders.append({
                                'name': name,
                                'linkedin': linkedin_url,
                                'role': role
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error extracting founder data from link: {e}")
                        continue
            else:
                logger.info("No founder container found")
                    
        except Exception as e:
            logger.warning(f"Error in extract_founders: {e}")
            
        return founders
    
    def extract_investors(self, soup) -> List[Dict]:
        """Extract investor information using CSS selectors"""
        investors = []
        
        try:
            # Use the specific investor section selector
            investor_container = soup.select_one('.mb-0 > div:nth-child(8) > div:nth-child(2) > div:nth-child(2)')
            
            if investor_container:
                # Find all LinkedIn links within the investor container only
                investor_links = investor_container.find_all('a', href=lambda href: href and 'linkedin.com' in href)
                
                for link in investor_links:
                    try:
                        linkedin_url = clean_url(link.get('href', ''))
                        
                        # Extract name from first p element within the link
                        name_element = link.select_one('div > div > p:nth-child(1)')
                        name = name_element.get_text(strip=True) if name_element else ""
                        
                        if name:
                            # Determine investor type based on LinkedIn URL
                            investor_type = 'VC_Firm' if '/company/' in linkedin_url else 'Angel_Syndicate'
                            
                            investors.append({
                                'name': name,
                                'linkedin': linkedin_url,
                                'type': investor_type
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error extracting investor data from link: {e}")
                        continue
            else:
                logger.info("No investor container found")
                        
        except Exception as e:
            logger.warning(f"Error in extract_investors: {e}")
            
        return investors
    
    def scrape_all_startups(self, max_pages: int = None, max_startups: int = None) -> List[StartupData]:
        """
        Scrape all startups from C14.so
        """
        logger.info("Starting C14.so scraping...")
        
        # Get all startup links first
        startup_links = self.get_startup_links(max_pages)
        
        if max_startups:
            startup_links = startup_links[:max_startups]
        
        startups_data = []
        
        for i, (name, desc, url, uuid) in enumerate(startup_links, 1):
            logger.info(f"Scraping startup {i}/{len(startup_links)}: {name}")
            
            startup_data = self.scrape_startup_details(url, uuid)
            if startup_data:
                # Use the name and description from the list page if detailed scraping didn't get them
                if not startup_data.name:
                    startup_data.name = name
                if not startup_data.description:
                    startup_data.description = desc
                    
                startups_data.append(startup_data)
            
            # Rate limiting
            time.sleep(self.delay)
        
        logger.info(f"Successfully scraped {len(startups_data)} startups")
        return startups_data
    
    def save_to_csv(self, startups: List[StartupData], filename: str = "c14_startups.csv"):
        """
        Save scraped startup data to CSV format compatible with our CSV importer
        """
        import pandas as pd
        
        data = []
        for startup in startups:
            # Convert to our Startup entity format
            row = {
                'name': startup.name,
                'description': startup.description,
                'website': startup.website,
                'founded_year': self._extract_year(startup.foundation_date),
                'stage': startup.funding_stage if startup.funding_stage != 'Unknown' else '',
                'sector': ', '.join(startup.sectors),
                'business_model': '',
                'headquarters': startup.location,
                'employee_count': startup.team_size,
                'status': 'active',
                'total_funding': self._extract_funding_amount(startup.amount_raised),
                'last_funding_date': '',
                'exit_date': '',
                'exit_value': ''
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        # Use pipe separator to avoid issues with commas and semicolons in descriptions
        df.to_csv(filename, index=False, sep='|')
        logger.info(f"Saved {len(data)} startups to {filename}")
        
        return filename
    
    def save_founders_to_csv(self, filename: str = "c14_founders.csv"):
        """Save founder data to CSV format for Person entity import"""
        import pandas as pd
        
        data = []
        for founder in self.all_founders:
            # Split name into name and surname
            name_parts = founder['name'].split(' ', 1)
            first_name = name_parts[0] if name_parts else founder['name']
            surname = name_parts[1] if len(name_parts) > 1 else ""
            
            row = {
                'name': first_name,
                'surname': surname,
                'role_type': founder['role'],
                'linkedin_url': founder['linkedin'],
                'twitter_handle': '',
                'biography': '',
                'location': '',
                'birth_year': '',
                'education': '',
                'previous_experience': '',
                'specialization': founder['role'],
                'reputation_score': ''
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, sep='|')
        logger.info(f"Saved {len(data)} founders to {filename}")
        return filename
    
    def save_investors_to_csv(self, filename: str = "c14_investors.csv"):
        """Save investor data to CSV format for VC_Firm entity import"""
        import pandas as pd
        
        data = []
        for investor in self.all_investors:
            row = {
                'name': investor['name'],
                'description': '',
                'website': '',
                'founded_year': '',
                'headquarters': '',
                'type': investor['type'],
                'investment_focus': '',
                'stage_focus': '',
                'geographic_focus': '',
                'team_size': '',
                'assets_under_management': '',
                'portfolio_companies_count': ''
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, sep='|')
        logger.info(f"Saved {len(data)} investors to {filename}")
        return filename
    
    def save_founding_relationships_to_csv(self, filename: str = "c14_founding_relationships.csv"):
        """Save founding relationships to CSV"""
        import pandas as pd
        
        df = pd.DataFrame(self.founding_relationships)
        df.to_csv(filename, index=False, sep='|')
        logger.info(f"Saved {len(self.founding_relationships)} founding relationships to {filename}")
        return filename
    
    def save_investment_relationships_to_csv(self, filename: str = "c14_investment_relationships.csv"):
        """Save investment relationships to CSV"""
        import pandas as pd
        
        df = pd.DataFrame(self.investment_relationships)
        df.to_csv(filename, index=False, sep='|')
        logger.info(f"Saved {len(self.investment_relationships)} investment relationships to {filename}")
        return filename
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string"""
        if not date_str:
            return None
        
        # Look for 4-digit year
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return int(year_match.group())
        return None
    
    def _extract_employee_count(self, team_size_str: str) -> Optional[int]:
        """Extract employee count from team size string"""
        if not team_size_str:
            return None
        
        # Handle ranges like "501-1000"
        if '-' in team_size_str:
            parts = team_size_str.split('-')
            try:
                # Return the midpoint of the range
                min_val = int(parts[0])
                max_val = int(parts[1])
                return (min_val + max_val) // 2
            except:
                pass
        
        # Extract single number
        number_match = re.search(r'\d+', team_size_str)
        if number_match:
            return int(number_match.group())
        
        return None
    
    def _extract_funding_amount(self, amount_str: str) -> Optional[float]:
        """Extract funding amount from amount string"""
        if not amount_str:
            return None
        
        # Remove currency symbols and convert to float
        amount_clean = re.sub(r'[^\d.,]', '', amount_str)
        if not amount_clean:
            return None
        
        try:
            # Handle different decimal separators
            amount_clean = amount_clean.replace(',', '.')
            return float(amount_clean)
        except:
            return None

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape C14.so startup database')
    parser.add_argument('--max-pages', type=int, help='Maximum pages to scrape')
    parser.add_argument('--max-startups', type=int, help='Maximum startups to scrape')
    parser.add_argument('--output', default='c14_startups.csv', help='Output CSV file')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create scraper and run
    scraper = C14Scraper(delay=args.delay)
    startups = scraper.scrape_all_startups(max_pages=args.max_pages, max_startups=args.max_startups)
    
    if startups:
        # Save startup data
        scraper.save_to_csv(startups, args.output)
        print(f"Successfully scraped {len(startups)} startups to {args.output}")
        
        # Save founder and investor data
        base_name = args.output.replace('.csv', '')
        scraper.save_founders_to_csv(f"{base_name}_founders.csv")
        scraper.save_investors_to_csv(f"{base_name}_investors.csv")
        scraper.save_founding_relationships_to_csv(f"{base_name}_founding_relationships.csv")
        scraper.save_investment_relationships_to_csv(f"{base_name}_investment_relationships.csv")
        
        print(f"Also saved:")
        print(f"- {len(scraper.all_founders)} founders to {base_name}_founders.csv")
        print(f"- {len(scraper.all_investors)} investors to {base_name}_investors.csv")
        print(f"- {len(scraper.founding_relationships)} founding relationships to {base_name}_founding_relationships.csv")
        print(f"- {len(scraper.investment_relationships)} investment relationships to {base_name}_investment_relationships.csv")
    else:
        print("No startups scraped")
