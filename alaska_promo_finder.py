#!/usr/bin/env python3
"""
Alaska Airlines Fast Track Promo Finder

This script systematically searches for Alaska Airlines employer-specific
fast track promo URLs and extracts the associated company/university names.
"""

import requests
import re
import json
import time
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Set
import argparse
import logging
from datetime import datetime
import random

class AlaskaPromoFinder:
    def __init__(self, results_file: str = "alaska_promos.json", delay: float = 1.0):
        self.base_url = "https://www.alaskaair.com/promo/"
        self.results_file = results_file
        self.delay = delay
        self.results: Dict[str, Dict] = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Setup logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('alaska_promo_finder.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load existing results
        self.load_results()

    def load_results(self) -> None:
        """Load previously found results from file"""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    self.results = json.load(f)
                self.logger.info(f"Loaded {len(self.results)} existing results")
            except Exception as e:
                self.logger.error(f"Error loading results: {e}")
                self.results = {}

    def save_results(self) -> None:
        """Save results to file"""
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(self.results)} results to {self.results_file}")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")

    def generate_promo_codes(self) -> List[str]:
        """Generate possible promo codes based on observed patterns"""
        codes = [f"{i:02}" for i in range(100)]
        prefixes = ["AS23", "CS23", "AS24", "CS24", "AS25", "CS25"]
        all_codes = []
        for prefix in prefixes:
            for code in codes:
                all_codes.append(f"{prefix}{code}")
        return all_codes

    def extract_company_name(self, html_content: str) -> Optional[str]:
        """Extract company/university name from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Method 1: Look for company_name in script data
            scripts = soup.find_all('script', {'type': 'application/json'})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if 'props' in data and 'pageProps' in data['props']:
                        content = data['props']['pageProps'].get('content', {})
                        company_name = content.get('company_name')
                        if company_name:
                            return company_name
                        
                        # Also check promo_data
                        promo_data = data['props']['pageProps'].get('promo_data', {})
                        company_name = promo_data.get('company_name')
                        if company_name:
                            return company_name
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Method 2: Look for email validation patterns
            email_patterns = [
                r'@(\w+)\.edu',
                r'@(\w+)\.com',
                r'@(\w+)\.org',
                r'university\s+of\s+(\w+)',
                r'(\w+)\s+university'
            ]
            
            text_content = soup.get_text().lower()
            for pattern in email_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    return matches[0].title()
            
            # Method 3: Look for specific text patterns
            company_indicators = [
                r'Only.*?members who work at ([^,]+)',
                r'([^,]+) discover a quicker way',
                r'([^,]+) employees',
                r'([^,]+) staff'
            ]
            
            for pattern in company_indicators:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    return matches[0].strip().title()
                    
        except Exception as e:
            self.logger.error(f"Error extracting company name: {e}")
            
        return None

    def check_promo_url(self, promo_code: str) -> Optional[Dict]:
        """Check if a promo URL exists and extract information"""
        url = urljoin(self.base_url, promo_code)
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Check if it's a valid promo page (not a generic error page)
                if 'fast track' in response.text.lower() or 'mileage plan' in response.text.lower():
                    company_name = self.extract_company_name(response.text)
                    
                    # Check if the promotion is expired
                    status = 'active'
                    expiration_info = None
                    
                    # Check for explicit expiration messages
                    if 'promotion ended' in response.text.lower() or 'expired' in response.text.lower():
                        status = 'expired'
                        # Try to extract expiration date from the text
                        expiration_match = re.search(r'promotion ended.*?on\s+(\d{1,2}/\d{1,2}/\d{4})', response.text, re.IGNORECASE)
                        if expiration_match:
                            expiration_info = expiration_match.group(1)
                    
                    # Also check JSON data for end_date
                    try:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        scripts = soup.find_all('script', {'type': 'application/json'})
                        for script in scripts:
                            try:
                                data = json.loads(script.string)
                                if 'props' in data and 'pageProps' in data['props']:
                                    promo_data = data['props']['pageProps'].get('promo_data', {})
                                    end_date = promo_data.get('end_date')
                                    if end_date:
                                        # Check if end date is in the past
                                        try:
                                            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                                            if end_datetime < datetime.now().astimezone():
                                                status = 'expired'
                                                if not expiration_info:
                                                    expiration_info = end_datetime.strftime('%m/%d/%Y')
                                        except ValueError:
                                            pass
                            except (json.JSONDecodeError, KeyError):
                                continue
                    except Exception:
                        pass
                    
                    result = {
                        'promo_code': promo_code,
                        'url': url,
                        'company_name': company_name,
                        'found_date': datetime.now().isoformat(),
                        'status': status  # Now properly set to 'expired' when detected
                    }
                    
                    if expiration_info:
                        result['expiration_date'] = expiration_info
                    
                    status_emoji = "⏰" if status == 'expired' else "✅"
                    status_text = f"({status.upper()})" if status == 'expired' else ""
                    self.logger.info(f"{status_emoji} Found: {promo_code} - {company_name or 'Unknown Company'} {status_text}")
                    return result
                else:
                    self.logger.debug(f"❌ {promo_code} - Not a valid promo page")
            else:
                self.logger.debug(f"❌ {promo_code} - HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ {promo_code} - Request failed: {e}")
        
        return None

    def search_promos(self, max_codes: Optional[int] = None, start_from: Optional[str] = None) -> None:
        """Search for promo codes"""
        codes = self.generate_promo_codes()
        
        if start_from:
            try:
                start_index = codes.index(start_from)
                codes = codes[start_index:]
                self.logger.info(f"Starting from code: {start_from}")
            except ValueError:
                self.logger.warning(f"Start code {start_from} not found, starting from beginning")
        
        if max_codes:
            codes = codes[:max_codes]
        
        self.logger.info(f"Searching {len(codes)} promo codes...")
        
        found_count = 0
        for i, code in enumerate(codes):
            # Skip if already checked
            if code in self.results:
                continue
                
            self.logger.info(f"[{i+1}/{len(codes)}] Checking {code}...")
            
            result = self.check_promo_url(code)
            if result:
                self.results[code] = result
                found_count += 1
                
                # Save results periodically
                if found_count % 5 == 0:
                    self.save_results()
            
            # Rate limiting
            time.sleep(random.uniform(0.5, 1.5) * self.delay)
        
        self.save_results()
        self.logger.info(f"Search complete! Found {found_count} new promos")

    def search_by_company(self, company_query: str) -> List[Dict]:
        """Search for promos by company name"""
        matches = []
        query_lower = company_query.lower()
        
        for code, data in self.results.items():
            if data.get('company_name'):
                if query_lower in data['company_name'].lower():
                    matches.append(data)
        
        return matches

    def list_all_promos(self) -> None:
        """List all found promos"""
        if not self.results:
            print("No promos found yet. Run search first.")
            return
        
        print(f"\n🎯 Found {len(self.results)} Alaska Airlines Fast Track Promos:\n")
        print(f"{'Code':<8} {'Company':<35} {'Status':<12} {'URL'}")
        print("-" * 95)
        
        for code, data in sorted(self.results.items()):
            company = data.get('company_name', 'Unknown')[:33]
            status = data.get('status', 'unknown')
            status_display = "⏰ EXPIRED" if status == 'expired' else "✅ ACTIVE"
            url = data.get('url', '')
            print(f"{code:<8} {company:<35} {status_display:<12} {url}")

def main():
    parser = argparse.ArgumentParser(description='Find Alaska Airlines fast track promo URLs')
    parser.add_argument('--search', action='store_true', help='Search for new promo codes')
    parser.add_argument('--company', type=str, help='Search for specific company')
    parser.add_argument('--list', action='store_true', help='List all found promos')
    parser.add_argument('--max-codes', type=int, help='Maximum number of codes to check')
    parser.add_argument('--start-from', type=str, help='Start searching from specific code')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--results-file', type=str, default='alaska_promos.json', help='Results file')
    
    args = parser.parse_args()
    
    finder = AlaskaPromoFinder(results_file=args.results_file, delay=args.delay)
    
    if args.search:
        finder.search_promos(max_codes=args.max_codes, start_from=args.start_from)
    elif args.company:
        matches = finder.search_by_company(args.company)
        if matches:
            print(f"\n🎯 Found {len(matches)} matches for '{args.company}':")
            for match in matches:
                print(f"  {match['promo_code']}: {match['company_name']} - {match['url']}")
        else:
            print(f"No matches found for '{args.company}'")
    elif args.list:
        finder.list_all_promos()
    else:
        print("Usage examples:")
        print("  python alaska_promo_finder.py --search")
        print("  python alaska_promo_finder.py --search --max-codes 100")
        print("  python alaska_promo_finder.py --company 'Microsoft'")
        print("  python alaska_promo_finder.py --list")

if __name__ == "__main__":
    main() 