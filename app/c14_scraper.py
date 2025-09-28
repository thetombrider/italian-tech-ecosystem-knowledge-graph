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
from urllib.parse import urljoin, urlparse
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

class C14Scraper:
    """Scraper for C14.so Italian startup database"""
    
    def __init__(self, delay: float = 1.0):
        self.base_url = "https://www.c14.so"
        self.delay = delay  # Rate limiting
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
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
            
            # Description (usually after the title)
            desc_candidates = soup.find_all(['p', 'div'], string=re.compile(r'.{20,}'))
            for candidate in desc_candidates:
                text = candidate.get_text(strip=True)
                if len(text) > 20 and not text.startswith('http'):
                    description = text
                    break
            
            # Links (website, linkedin)
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                if 'visit website' in text or 'website' in text:
                    website = href
                elif 'linkedin' in text or 'linkedin.com' in href:
                    linkedin = href
            
            # Company details (usually in sidebar or info section)
            location = ""
            foundation_date = ""
            team_size = ""
            funding_stage = ""
            amount_raised = ""
            
            # Look for structured data
            info_elements = soup.find_all(['dt', 'dd', 'div', 'span'])
            current_field = None
            
            for element in info_elements:
                text = element.get_text(strip=True)
                
                if 'location' in text.lower():
                    current_field = 'location'
                elif 'foundation' in text.lower() or 'founded' in text.lower():
                    current_field = 'foundation_date'
                elif 'team size' in text.lower():
                    current_field = 'team_size'
                elif 'funding stage' in text.lower():
                    current_field = 'funding_stage'
                elif 'amount raised' in text.lower() or 'raised' in text.lower():
                    current_field = 'amount_raised'
                elif current_field and not any(word in text.lower() for word in ['location', 'foundation', 'team', 'funding', 'amount']):
                    if current_field == 'location':
                        location = text
                    elif current_field == 'foundation_date':
                        foundation_date = text
                    elif current_field == 'team_size':
                        team_size = text
                    elif current_field == 'funding_stage':
                        funding_stage = text
                    elif current_field == 'amount_raised':
                        amount_raised = text
                    current_field = None
            
            # Extract sectors from page content or links
            sectors = []
            sector_candidates = soup.find_all(['span', 'div', 'a'], class_=re.compile(r'tag|category|sector'))
            for candidate in sector_candidates:
                sector_text = candidate.get_text(strip=True)
                if sector_text and len(sector_text) < 50:
                    sectors.append(sector_text)
            
            # Extract team members
            team_members = []
            team_section = soup.find(['div', 'section'], string=re.compile(r'team', re.I))
            if team_section:
                team_links = team_section.find_next_siblings() or team_section.find_all('a', href=re.compile(r'linkedin'))
                for link in team_links[:10]:  # Limit to avoid too much data
                    member_name = link.get_text(strip=True)
                    member_linkedin = link.get('href', '')
                    if member_name and 'linkedin' in member_linkedin:
                        team_members.append({
                            'name': member_name,
                            'linkedin': member_linkedin,
                            'role': ''  # Could be extracted if available
                        })
            
            # Extract investors
            investors = []
            investor_section = soup.find(['div', 'section'], string=re.compile(r'investor', re.I))
            if investor_section:
                investor_links = investor_section.find_next_siblings() or investor_section.find_all('a', href=re.compile(r'linkedin'))
                for link in investor_links[:10]:  # Limit to avoid too much data
                    investor_name = link.get_text(strip=True)
                    investor_linkedin = link.get('href', '')
                    if investor_name and 'linkedin' in investor_linkedin:
                        investors.append({
                            'name': investor_name,
                            'linkedin': investor_linkedin,
                            'type': 'unknown'
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
                'employee_count': self._extract_employee_count(startup.team_size),
                'status': 'active',
                'total_funding': self._extract_funding_amount(startup.amount_raised),
                'last_funding_date': '',
                'exit_date': '',
                'exit_value': ''
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(data)} startups to {filename}")
        
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
        scraper.save_to_csv(startups, args.output)
        print(f"Successfully scraped {len(startups)} startups to {args.output}")
    else:
        print("No startups scraped")
