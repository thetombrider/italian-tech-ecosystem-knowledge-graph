#!/usr/bin/env python3
"""
Test script per verificare i selettori CSS sulla pagina di 4books
"""

import requests
from bs4 import BeautifulSoup

def test_selectors():
    url = "https://www.c14.so/2e45ff9b-d40d-431c-ba1c-25824eaa9174"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== Testing CSS Selectors ===")
        
        # Test current selector
        print("\n1. Current selector: div.border-default:nth-child(1) > div:nth-child(1) > p:nth-child(2)")
        current_element = soup.select_one('div.border-default:nth-child(1) > div:nth-child(1) > p:nth-child(2)')
        if current_element:
            print(f"Result: '{current_element.get_text(strip=True)}'")
        else:
            print("No result found")
        
        # Try alternative selectors
        alternative_selectors = [
            'div.border-default:nth-child(1) > div:nth-child(2) > p:nth-child(2)',
            'div.border-default:nth-child(2) > div:nth-child(1) > p:nth-child(2)',
            'div.border-default:nth-child(2) > div:nth-child(2) > p:nth-child(2)',
        ]
        
        for i, selector in enumerate(alternative_selectors, 2):
            print(f"\n{i}. Alternative selector: {selector}")
            element = soup.select_one(selector)
            if element:
                print(f"Result: '{element.get_text(strip=True)}'")
            else:
                print("No result found")
        
        # Search for text containing "11-50"
        print("\n=== Searching for elements containing '11-50' ===")
        all_elements = soup.find_all(text=lambda text: text and '11-50' in text)
        for i, text in enumerate(all_elements):
            parent = text.parent
            print(f"Found '{text.strip()}' in tag: {parent.name} with classes: {parent.get('class', [])}")
            
        # Check all div.border-default elements
        print("\n=== All div.border-default elements ===")
        border_divs = soup.select('div.border-default')
        for i, div in enumerate(border_divs):
            print(f"div.border-default:nth-child({i+1}):")
            print(f"  Content: {div.get_text(strip=True)[:100]}...")
            # Check child divs
            child_divs = div.find_all('div', recursive=False)
            for j, child_div in enumerate(child_divs):
                print(f"    div:nth-child({j+1}): {child_div.get_text(strip=True)[:50]}...")
                # Check p elements in child div
                p_elements = child_div.find_all('p', recursive=False)
                for k, p in enumerate(p_elements):
                    print(f"      p:nth-child({k+1}): '{p.get_text(strip=True)}'")
            print()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_selectors()
