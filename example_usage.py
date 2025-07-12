#!/usr/bin/env python3
"""
Example usage of the Alaska Airlines Fast Track Promo Finder

This script demonstrates how to use the AlaskaPromoFinder class
programmatically to search for and find company-specific promo codes.
"""

from alaska_promo_finder import AlaskaPromoFinder

def main():
    # Create finder instance
    finder = AlaskaPromoFinder(delay=1.5)  # 1.5 second delay between requests
    
    print("🔍 Alaska Airlines Fast Track Promo Finder")
    print("=" * 50)
    
    # Example 1: Search for a small number of codes (good for testing)
    print("\n1. Searching first 10 codes as a test...")
    finder.search_promos(max_codes=10)
    
    # Example 2: Search for a specific company
    print("\n2. Searching for 'Microsoft' in found results...")
    microsoft_matches = finder.search_by_company("Microsoft")
    if microsoft_matches:
        for match in microsoft_matches:
            print(f"   Found: {match['promo_code']} - {match['url']}")
    else:
        print("   No Microsoft promos found yet.")
    
    # Example 3: Search for universities
    print("\n3. Searching for 'University' in found results...")
    university_matches = finder.search_by_company("University")
    if university_matches:
        for match in university_matches:
            print(f"   Found: {match['promo_code']} - {match['company_name']}")
    else:
        print("   No university promos found yet.")
    
    # Example 4: List all found promos
    print("\n4. All found promos:")
    finder.list_all_promos()
    
    print("\n✅ Example complete!")
    print("To run a full search, use:")
    print("   python alaska_promo_finder.py --search")

if __name__ == "__main__":
    main() 