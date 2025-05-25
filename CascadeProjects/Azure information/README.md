# Microsoft Services Updates Dashboard

This application aggregates and displays the latest updates and changes from various Microsoft services including:
- Azure Updates
- Microsoft 365
- Intune
- Azure Virtual Desktop
- Microsoft Defender

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:8000`

## Features

- Real-time fetching of updates from official Microsoft sources
- Clean, responsive web interface
- Updates are sorted by date
- Links to original documentation for each update
- Categorized by service
- Automatic refresh on page load

## Technology Stack

- FastAPI for the backend
- Jinja2 for templating
- TailwindCSS for styling
- Beautiful Soup for parsing documentation
- Feedparser for RSS feeds
