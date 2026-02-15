# Event Ticket Scraper (Ticketmaster)

Search concerts, sports games, theater shows, and live events via the **Ticketmaster Discovery API**. Get event details, ticket prices, venue info, presale dates, seat maps, and direct ticket links as clean JSON.

Works as a standalone scraper **and** as an MCP tool for AI agents.

## What data can you extract?

| Field | Example |
|-------|---------|
| Event name | "Taylor Swift \| The Eras Tour" |
| Date & time | 2025-08-15, 19:00:00, America/New_York |
| Ticket status | onsale, offsale, canceled, postponed, rescheduled |
| Price range | $49.50 - $449.50 USD |
| Venue | Madison Square Garden, New York, NY |
| Venue coordinates | 40.7505, -73.9934 |
| Artists/attractions | ["Taylor Swift"] |
| Classification | Music > Pop > Pop Rock |
| Public sale window | 2025-01-15T10:00:00Z - 2025-08-15T18:00:00Z |
| Presales | Verified Fan, Citi Cardmember, VIP packages |
| Ticket URL | Direct link to buy tickets |
| Seat map | Static seat map image URL |
| Event images | Multiple resolutions |
| Promoter | Live Nation |

## Use cases

- **Price monitoring** -- Track ticket price ranges for events over time
- **Event discovery** -- Find upcoming concerts, sports, theater in any city
- **Market research** -- Analyze event pricing across venues, genres, or regions
- **Alerting** -- Monitor presale dates and on-sale windows for hot events
- **Venue analysis** -- Research venue details, capacity, and upcoming event counts
- **AI agents** -- Feed event data into LLM pipelines via MCP integration

## Modes

### 1. Search events (default)

Search events by keyword, location, date range, classification, and more. Returns up to 1000 results per search (Ticketmaster API deep paging limit).

### 2. Get event by ID

Look up a specific event by its Ticketmaster event ID for full details including pricing, presales, and seat map.

### 3. Search venues

Search venues by keyword and location. Returns venue details including address, coordinates, parking info, and upcoming event count.

## API key (free)

This actor requires a **free** Ticketmaster Discovery API key:

1. Go to [developer.ticketmaster.com](https://developer.ticketmaster.com/)
2. Create a free account
3. Your API key is on the dashboard

Rate limits: 5000 calls/day, 5 requests/second. More than enough for typical use.

## Input examples

### Search for concerts in New York

```json
{
    "apiKey": "YOUR_API_KEY",
    "mode": "search",
    "keyword": "Taylor Swift",
    "city": "New York",
    "stateCode": "NY",
    "countryCode": "US",
    "classificationName": "Music",
    "maxResults": 50
}
```

### Find NBA games this month

```json
{
    "apiKey": "YOUR_API_KEY",
    "mode": "search",
    "keyword": "NBA",
    "startDateTime": "2025-06-01T00:00:00Z",
    "endDateTime": "2025-06-30T23:59:59Z",
    "countryCode": "US",
    "sort": "date,asc",
    "maxResults": 100
}
```

### Look up a specific event

```json
{
    "apiKey": "YOUR_API_KEY",
    "mode": "get_event",
    "eventId": "vvG1iZ4JFSmpkV"
}
```

### Search venues in Los Angeles

```json
{
    "apiKey": "YOUR_API_KEY",
    "mode": "venues",
    "keyword": "arena",
    "city": "Los Angeles",
    "stateCode": "CA"
}
```

### Events near a location (geo search)

```json
{
    "apiKey": "YOUR_API_KEY",
    "mode": "search",
    "latlong": "40.7128,-74.0060",
    "radius": 25,
    "unit": "miles",
    "classificationName": "Music",
    "sort": "distance,asc",
    "maxResults": 50
}
```

## Output example

Each event is one dataset item:

```json
{
    "schema_version": "1.0",
    "type": "event",
    "event_name": "Taylor Swift | The Eras Tour",
    "event_id": "vvG1iZ4JFSmpkV",
    "event_url": "https://www.ticketmaster.com/event/vvG1iZ4JFSmpkV",
    "local_date": "2025-08-15",
    "local_time": "19:00:00",
    "datetime_utc": "2025-08-15T23:00:00Z",
    "timezone": "America/New_York",
    "status": "onsale",
    "price_min": 49.5,
    "price_max": 449.5,
    "price_currency": "USD",
    "venue_name": "Madison Square Garden",
    "venue_id": "KovZpZA7AAEA",
    "venue_city": "New York",
    "venue_state": "New York",
    "venue_country": "United States Of America",
    "venue_address": "4 Pennsylvania Plaza",
    "venue_postal_code": "10001",
    "venue_latitude": 40.7505,
    "venue_longitude": -73.9934,
    "attractions": ["Taylor Swift"],
    "segment": "Music",
    "genre": "Pop",
    "sub_genre": "Pop Rock",
    "public_sale_start": "2025-01-15T15:00:00Z",
    "public_sale_end": "2025-08-15T23:00:00Z",
    "presales": [
        {
            "name": "Verified Fan Presale",
            "start_date_time": "2025-01-13T15:00:00Z",
            "end_date_time": "2025-01-14T23:00:00Z",
            "description": "",
            "url": ""
        }
    ],
    "promoter": "Live Nation",
    "seatmap_url": "https://maps.ticketmaster.com/...",
    "images": ["https://s1.ticketm.net/dam/a/..."],
    "info": "",
    "please_note": "No professional cameras or recording devices",
    "ticket_limit": "There is a 4 ticket limit per household",
    "accessibility_info": "",
    "source": "ticketmaster",
    "scraped_at": "2025-06-15T12:00:00+00:00"
}
```

## Input parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `apiKey` | string | *required* | Ticketmaster Discovery API key (free) |
| `mode` | string | `"search"` | `search`, `get_event`, or `venues` |
| `keyword` | string | | Search term (artist, event, team, genre) |
| `eventId` | string | | Event ID for `get_event` mode |
| `city` | string | | Filter by city |
| `stateCode` | string | | State/province code (e.g. `NY`, `CA`) |
| `countryCode` | string | | Country code (e.g. `US`, `GB`, `CA`) |
| `postalCode` | string | | Postal/zip code |
| `latlong` | string | | Lat,long for geo search (e.g. `40.7128,-74.0060`) |
| `radius` | integer | | Search radius (use with `latlong` or `postalCode`) |
| `unit` | string | `"miles"` | Radius unit: `miles` or `km` |
| `classificationName` | string | | Event type: `Music`, `Sports`, `Arts & Theatre`, etc. |
| `startDateTime` | string | | Events after this date (ISO 8601 with Z) |
| `endDateTime` | string | | Events before this date (ISO 8601 with Z) |
| `sort` | string | `"relevance,desc"` | Sort order |
| `source` | string | | Filter by source platform |
| `includeFamily` | string | | Family-friendly filter: `yes` or `no` |
| `maxResults` | integer | `100` | Max results (1-1000). Free tier: 25 |
| `requestIntervalSecs` | number | `0.5` | Seconds between API requests |

## Limitations

- **Deep paging**: Ticketmaster limits results to ~1000 per search query. Use filters to narrow results.
- **Price ranges**: The API provides price ranges (min/max), not individual seat prices.
- **Availability**: The API does not provide real-time seat-level availability.
- **Rate limits**: 5000 API calls/day, 5 requests/second (free tier API key).
- **Geography**: Best coverage for US, Canada, UK, and select European markets.

## Cost

This actor uses **pay-per-event** pricing at **$0.0005 per event** (that's $0.50 per 1000 events).

Free tier users get **25 results per run** at no cost.

## MCP integration

Use this actor as a tool in your AI agent pipeline. Add to your MCP client config:

```json
{
    "mcpServers": {
        "apify": {
            "command": "npx",
            "args": ["-y", "@apify/actors-mcp-server"],
            "env": {
                "APIFY_TOKEN": "your-apify-token"
            }
        }
    }
}
```

Then ask your AI: *"Find Taylor Swift concerts in New York with ticket prices"*

## Technical details

- **No browser needed** -- pure API-based, no Playwright/Puppeteer
- **Python 3.12** on the `apify/actor-python:3.12` Docker image
- **Resumable** -- uses Apify state persistence for long runs
- **Batch push** -- pushes results in batches of 25 for efficiency
- **Rate limiting** -- built-in rate limiter with configurable interval
- **Retry logic** -- automatic retry with exponential backoff on 429 responses
