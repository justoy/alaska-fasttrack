# Alaska Airlines Fast Track Promo Finder

This project automates the discovery of employer-specific fast-track promo links provided by Alaska Airlines. Alaska Airlines offers special URLs for companies and universities to help employees or affiliates quickly achieve loyalty program status. However, these URLs are not publicly listed.

This tool systematically scans possible promo-code URLs, identifies valid ones, extracts the associated employer or university names, and stores the results. The primary goal is to enable users to easily find their organization's fast-track link without manual guessing.

## Examples

- University of Washington: https://www.alaskaair.com/promo/CS2344
- Microsoft: https://www.alaskaair.com/promo/AS2366

## Installation

1. Install Python 3.7+ if not already installed
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Search for new promo codes
```bash
# Search all possible codes (this will take a while!)
python alaska_promo_finder.py --search

# Search first 100 codes only (good for testing)
python alaska_promo_finder.py --search --max-codes 100

# Start from a specific code
python alaska_promo_finder.py --search --start-from CS2300

# Increase delay between requests (be respectful!)
python alaska_promo_finder.py --search --delay 2.0
```

### Search for your company
```bash
# Search for your company in found results
python alaska_promo_finder.py --company "Microsoft"
python alaska_promo_finder.py --company "University"
python alaska_promo_finder.py --company "Amazon"
```

### List all found promos
```bash
python alaska_promo_finder.py --list
```

## Features

- **Persistent Storage**: Results are saved to `alaska_promos.json` and can be resumed
- **Progress Tracking**: Real-time progress updates and logging
- **Company Extraction**: Automatically extracts company/university names from promo pages
- **Rate Limiting**: Respects servers with configurable delays
- **Multiple Search Patterns**: Covers CS, AS, and MS prefix patterns
- **Flexible Search**: Find promos by company name or list all results

## Output Files

- `alaska_promos.json`: Found promo codes with company information
- `alaska_promo_finder.log`: Detailed log of search progress

## Promo Code Patterns

The script searches for patterns like:
- `CS20XX` to `CS29XX` (Corporate Sales)
- `AS20XX` to `AS29XX` (Alaska Sales)  
- `MS20XX` to `MS29XX` (Microsoft Sales)

## Ethical Usage

Please use this tool responsibly:
- Use reasonable delays between requests (default 1 second)
- Don't overwhelm Alaska Airlines' servers
- Only use found promo codes if you're eligible (work at the company)
- This tool is for discovery purposes only
