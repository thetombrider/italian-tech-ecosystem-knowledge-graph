#!/usr/bin/env python3
"""
Analizza la struttura delle sezioni founder/investor su 4books
"""

import requests
from bs4 import BeautifulSoup

def analyze_sections():
    url = "https://www.c14.so/2e45ff9b-d40d-431c-ba1c-25824eaa9174"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== Analisi Sezioni Founder/Investor ===\n")
        
        # Cerchiamo elementi che contengono "team" o "founder"
        print("1. Elementi con testo 'team' o 'Meet the team':")
        team_elements = soup.find_all(text=lambda text: text and ('team' in text.lower() or 'founder' in text.lower()))
        for i, elem in enumerate(team_elements[:5]):
            parent = elem.parent
            print(f"   [{i}] Testo: '{elem.strip()}'")
            print(f"       Parent: {parent.name} - Classes: {parent.get('class', [])}")
            print(f"       CSS Path approx: {parent.name}")
            print()
        
        # Cerchiamo elementi che contengono "investor"  
        print("2. Elementi con testo 'investor' o 'Meet the investors':")
        investor_elements = soup.find_all(text=lambda text: text and 'investor' in text.lower())
        for i, elem in enumerate(investor_elements[:5]):
            parent = elem.parent
            print(f"   [{i}] Testo: '{elem.strip()}'")
            print(f"       Parent: {parent.name} - Classes: {parent.get('class', [])}")
            print()
            
        # Analizziamo la struttura intorno ai link LinkedIn
        print("3. Struttura intorno ai link LinkedIn:")
        linkedin_links = soup.find_all('a', href=lambda href: href and 'linkedin.com' in href)
        for i, link in enumerate(linkedin_links):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"   [{i}] Link: {href}")
            print(f"       Testo: '{text}'")
            
            # Troviamo il container padre più vicino
            container = link
            for _ in range(5):  # Risali fino a 5 livelli
                container = container.parent
                if container and container.name == 'div':
                    # Controlla se ha fratelli con altri link LinkedIn
                    siblings = container.find_all('a', href=lambda h: h and 'linkedin.com' in h)
                    if len(siblings) > 1:
                        print(f"       Container: {container.get('class', [])} - {len(siblings)} LinkedIn links")
                        break
            print()
            
        # Cerchiamo pattern di raggruppamento
        print("4. Analisi pattern di raggruppamento:")
        divs_with_multiple_linkedin = []
        for div in soup.find_all('div'):
            linkedin_in_div = div.find_all('a', href=lambda h: h and 'linkedin.com' in h)
            if len(linkedin_in_div) >= 2:
                divs_with_multiple_linkedin.append((div, linkedin_in_div))
                
        for i, (div, links) in enumerate(divs_with_multiple_linkedin[:3]):
            print(f"   Gruppo {i}: {len(links)} LinkedIn links")
            print(f"   Classes: {div.get('class', [])}")
            for link in links:
                name_elem = link.select_one('div > div > p:nth-child(1)')
                name = name_elem.get_text(strip=True) if name_elem else "N/A"
                print(f"     - {name}: {link.get('href', '')}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_sections()
