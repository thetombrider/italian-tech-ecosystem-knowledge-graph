#!/usr/bin/env python3
"""
Test dettagliato dei selettori CSS per 4books
"""

import requests
from bs4 import BeautifulSoup

def detailed_selector_test():
    url = "https://www.c14.so/2e45ff9b-d40d-431c-ba1c-25824eaa9174"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== Detailed CSS Selector Test ===")
        
        selectors = {
            "Headquarters": 'div.border-default:nth-child(2) > div:nth-child(2) > p:nth-child(2)',
            "Founded year": 'div.border-default:nth-child(2) > div:nth-child(3) > p:nth-child(2)', 
            "Employee count": 'div.border-default:nth-child(2) > div:nth-child(1) > p:nth-child(2)',
            "Funding stage": 'div.border-default:nth-child(3) > div:nth-child(1) > p:nth-child(2)',
            "Total funding": 'div.border-default:nth-child(3) > div:nth-child(2) > p:nth-child(2)'
        }
        
        for label, selector in selectors.items():
            element = soup.select_one(selector)
            if element:
                result = element.get_text(strip=True)
                print(f"{label}: '{result}' (selector: {selector})")
            else:
                print(f"{label}: NOT FOUND (selector: {selector})")
                
        print("\n=== All div.border-default elements with detailed structure ===")
        border_divs = soup.select('div.border-default')
        for i, div in enumerate(border_divs, 1):
            print(f"\ndiv.border-default:nth-child({i}):")
            child_divs = div.find_all('div', recursive=False)
            for j, child_div in enumerate(child_divs, 1):
                p_elements = child_div.find_all('p', recursive=False)
                if len(p_elements) >= 2:
                    label = p_elements[0].get_text(strip=True)
                    value = p_elements[1].get_text(strip=True)
                    print(f"  div:nth-child({j}) > p:nth-child(2): '{value}' (label: '{label}')")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    detailed_selector_test()
