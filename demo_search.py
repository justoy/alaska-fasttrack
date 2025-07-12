#!/usr/bin/env python3
"""
Demo script to search for the known CS2344 University of Washington promo code
"""

from alaska_promo_finder import AlaskaPromoFinder

def demo_search():
    print("🔍 Alaska Airlines Fast Track Promo Finder Demo")
    print("=" * 50)
    print("This demo will search for the known CS2344 code (University of Washington)")
    print()
    
    # Create finder with a longer delay to be respectful
    finder = AlaskaPromoFinder(delay=2.0)
    
    # Search starting from CS2344 with just 1 code
    print("Searching for CS2344...")
    finder.search_promos(max_codes=1, start_from="CS2344")
    
    # Show results
    print("\nSearch complete! Here are the results:")
    finder.list_all_promos()
    
    # Search for University of Washington
    print("\nSearching for 'University of Washington'...")
    matches = finder.search_by_company("University of Washington")
    if matches:
        print(f"✅ Found {len(matches)} matches:")
        for match in matches:
            print(f"   {match['promo_code']}: {match['company_name']}")
            print(f"   URL: {match['url']}")
    else:
        print("❌ No matches found")

if __name__ == "__main__":
    demo_search() 