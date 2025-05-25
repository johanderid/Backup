from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dateutil import parser
import json
from concurrent.futures import ThreadPoolExecutor
import re

app = FastAPI(title="Microsoft Services Updates Dashboard")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Sources for updates
SOURCES = {
    'Azure Updates': 'https://azurecomcdn.azureedge.net/en-us/updates/feed/',
    'Microsoft 365': 'https://www.microsoft.com/en-us/microsoft-365/roadmap/feed',
    'Intune': 'https://learn.microsoft.com/en-us/mem/intune/fundamentals/whats-new',
    'Azure Virtual Desktop': 'https://learn.microsoft.com/en-us/azure/virtual-desktop/whats-new',
    'Microsoft Defender': 'https://learn.microsoft.com/en-us/microsoft-365/security/defender/whats-new',
}

def fetch_url(url):
    try:
        response = requests.get(url, timeout=10)
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def parse_feed(url):
    if url.endswith('/feed/'):
        feed = feedparser.parse(url)
        updates = []
        for entry in feed.entries[:10]:  # Get latest 10 entries
            updates.append({
                'title': entry.title,
                'date': entry.published,
                'link': entry.link,
                'source': 'Azure Updates' if 'azure' in url.lower() else 'Microsoft 365',
                'description': entry.description
            })
        return updates
    return []

def parse_docs_page(content, source):
    if not content:
        return []
    
    soup = BeautifulSoup(content, 'html.parser')
    updates = []
    
    if source == 'Intune':
        for section in soup.find_all(['h2', 'h3']):
            if 'week of' in section.text.lower():
                next_ul = section.find_next('ul')
                description = next_ul.text if next_ul else ''
                updates.append({
                    'title': section.text,
                    'date': section.text.split('Week of')[-1].strip(),
                    'link': SOURCES[source],
                    'source': source,
                    'description': description
                })
    elif source in ['Azure Virtual Desktop', 'Microsoft Defender']:
        for section in soup.find_all(['h2']):
            if any(month in section.text.lower() for month in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']):
                next_ul = section.find_next('ul')
                description = next_ul.text if next_ul else ''
                updates.append({
                    'title': section.text,
                    'date': section.text,
                    'link': SOURCES[source],
                    'source': source,
                    'description': description
                })
    
    return updates[:10]  # Return latest 10 updates

def parse_date(date_str):
    try:
        # Try direct parsing first
        return parser.parse(date_str)
    except:
        try:
            # Handle "Month Day, Year" format with extra text
            import re
            # Extract date part (e.g., "February 5, 2025" from "February 5, 2025 (Service release 2501)")
            date_match = re.match(r'([A-Za-z]+ \d{1,2}, \d{4})', date_str)
            if date_match:
                return parser.parse(date_match.group(1))
            
            # Handle "Week of Month Day, Year" format
            week_match = re.match(r'Week of ([A-Za-z]+ \d{1,2}, \d{4})', date_str)
            if week_match:
                return parser.parse(week_match.group(1))
            
            return datetime.now(timezone.utc)  # Fallback to current date if parsing fails
        except:
            return datetime.now(timezone.utc)  # Fallback to current date if parsing fails

def get_all_updates():
    all_updates = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for source, url in SOURCES.items():
            if url.endswith('/feed/'):
                updates = parse_feed(url)
            else:
                content = fetch_url(url)
                updates = parse_docs_page(content, source)
            all_updates.extend(updates)
    
    # Sort by date
    all_updates.sort(key=lambda x: parse_date(x['date']), reverse=True)
    return all_updates

@app.get("/")
async def root(request: Request):
    updates = get_all_updates()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "updates": updates}
    )

@app.get("/api/updates")
async def get_updates():
    """API endpoint to get updates in JSON format"""
    updates = get_all_updates()
    return {"updates": updates}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
