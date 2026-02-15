# 🎫 Event Ticket Scraper (Ticketmaster)

> **The most comprehensive, reliable event ticket scraper for Apify — powered by the official Ticketmaster Discovery API**

## 🌟 Why Choose This Scraper?

The Event Ticket Scraper delivers production-ready event search capabilities with these advanced features:

**Comprehensive Event Search**: Search concerts, sports games, theater shows, comedy, festivals, and any live event across Ticketmaster's massive database. Filter by keyword, city, state, country, zip code, geographic coordinates, date range, genre, and more.

**Real-Time Ticket Pricing**: Get current price ranges (min/max) with currency, ticket status (onsale/offsale/canceled/postponed), public sale windows, and presale details — all from Ticketmaster's official API.

**Rich Venue & Artist Data**: Every event includes full venue details (name, address, city, state, country, GPS coordinates, timezone), artist/attraction names, event classifications (segment > genre > sub-genre), promoter info, seat maps, and high-res images.

**Multiple Search Modes**: Search events by keyword, look up a specific event by ID, or search venues independently. Three modes, one actor.

**Free API Key**: Uses Ticketmaster's free Discovery API (5000 calls/day, 5 req/sec). No paid API subscription required — just register at developer.ticketmaster.com.

**Enterprise-Grade Reliability**: Built-in rate limiting, exponential backoff on 429 responses, configurable request intervals, batch dataset push, and Apify state persistence for resumable runs.

## 🚀 Features

### Core Capabilities

- **Three Search Modes**: Event search, event lookup by ID, and venue search
- **Powerful Filters**: Keyword, city, state, country, postal code, lat/long radius, date range, genre/classification, source platform, family-friendly
- **Geo Search**: Search events within a radius of any GPS coordinate or postal code
- **Flexible Sorting**: By relevance, date (soonest/latest), name (A-Z/Z-A), or distance (nearest first)
- **Deep Pagination**: Automatic pagination up to Ticketmaster's 1000-result limit per search
- **Global Coverage**: US, Canada, UK, Mexico, and select European markets

### Data Quality

- **Ticket Pricing**: Min/max price ranges with currency for every event
- **Presale Intel**: Presale names, date windows, and descriptions (Verified Fan, Citi Cardmember, VIP, etc.)
- **Venue Details**: Full address, city, state, country, postal code, GPS coordinates, and timezone
- **Classification Hierarchy**: Segment > Genre > Sub-Genre (e.g. Music > Rock > Alternative Rock)
- **Rich Media**: Seat map images, event images in multiple resolutions
- **Direct Links**: Ticket purchase URLs for every event

## 📖 Usage Examples

### Example 1: Concert Search in New York

Search for Taylor Swift concerts in New York City.

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

### Example 2: Sports Events with Date Range

Find NBA games happening in June, sorted by date.

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

### Example 3: Geo Search — Events Near Me

Find music events within 25 miles of Manhattan.

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

### Example 4: Look Up a Specific Event

Get full details for a known Ticketmaster event ID.

```json
{
    "apiKey": "YOUR_API_KEY",
    "mode": "get_event",
    "eventId": "vvG1iZ4JFSmpkV"
}
```

### Example 5: Venue Search

Search for arenas in Los Angeles.

```json
{
    "apiKey": "YOUR_API_KEY",
    "mode": "venues",
    "keyword": "arena",
    "city": "Los Angeles",
    "stateCode": "CA"
}
```

### Example 6: Comedy Shows — Family-Friendly Only

Find family-friendly comedy shows in Chicago.

```json
{
    "apiKey": "YOUR_API_KEY",
    "mode": "search",
    "classificationName": "Comedy",
    "city": "Chicago",
    "stateCode": "IL",
    "includeFamily": "yes",
    "sort": "date,asc",
    "maxResults": 25
}
```

## 🔍 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `apiKey` | `string` | ✅ | - | Ticketmaster Discovery API key. Get one for free at [developer.ticketmaster.com](https://developer.ticketmaster.com/) |
| `mode` | `string` | ❌ | `"search"` | Operation mode: `search`, `get_event`, or `venues` |
| `keyword` | `string` | ❌ | - | Search term — artist, event name, team, or genre (e.g. `"Taylor Swift"`, `"NBA"`, `"comedy"`) |
| `eventId` | `string` | ❌ | - | Ticketmaster event ID for `get_event` mode (e.g. `"vvG1iZ4JFSmpkV"`) |
| `city` | `string` | ❌ | - | Filter by city name (e.g. `"New York"`, `"Los Angeles"`) |
| `stateCode` | `string` | ❌ | - | State/province code (e.g. `"NY"`, `"CA"`, `"ON"`) |
| `countryCode` | `string` | ❌ | - | ISO Alpha-2 country code (e.g. `"US"`, `"CA"`, `"GB"`) |
| `postalCode` | `string` | ❌ | - | Postal/zip code (e.g. `"10001"`) |
| `latlong` | `string` | ❌ | - | Geographic center point as `"lat,long"` (e.g. `"40.7128,-74.0060"`). Use with `radius` |
| `radius` | `integer` | ❌ | - | Search radius from center point, in miles or km (1–500) |
| `unit` | `string` | ❌ | `"miles"` | Radius unit: `miles` or `km` |
| `classificationName` | `string` | ❌ | - | Event type/genre: `"Music"`, `"Sports"`, `"Arts & Theatre"`, `"Comedy"`, `"Rock"`, `"Pop"`, `"NBA"`, `"NFL"`, etc. |
| `startDateTime` | `string` | ❌ | - | Events starting on or after this date. ISO 8601 format: `"YYYY-MM-DDTHH:mm:ssZ"` |
| `endDateTime` | `string` | ❌ | - | Events starting on or before this date. ISO 8601 format: `"YYYY-MM-DDTHH:mm:ssZ"` |
| `sort` | `string` | ❌ | `"relevance,desc"` | Sort order: `relevance,desc`, `date,asc`, `date,desc`, `name,asc`, `name,desc`, `distance,asc` |
| `source` | `string` | ❌ | - | Filter by source: `ticketmaster`, `universe`, `frontgate`, `tmr` |
| `includeFamily` | `string` | ❌ | - | Family-friendly filter: `"yes"` or `"no"` |
| `maxResults` | `integer` | ❌ | `100` | Maximum number of results (1–1000). Free tier users: 25 per run |
| `requestIntervalSecs` | `number` | ❌ | `0.5` | Minimum seconds between API requests (0.2–5.0) |

## 📊 Output Format

### Event Output

Each event is pushed as a separate dataset item with the following structure:

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

### Output Fields

- **`event_name`** / **`event_id`** / **`event_url`**: Core event identification and direct ticket link
- **`local_date`** / **`local_time`** / **`datetime_utc`** / **`timezone`**: Complete date/time information
- **`status`**: Current ticket status — `onsale`, `offsale`, `canceled`, `postponed`, `rescheduled`
- **`price_min`** / **`price_max`** / **`price_currency`**: Ticket price range
- **`venue_*`**: Full venue details including GPS coordinates
- **`attractions`**: Artist/team names associated with the event
- **`segment`** / **`genre`** / **`sub_genre`**: Event classification hierarchy
- **`presales`**: Array of presale windows with names, dates, and descriptions
- **`seatmap_url`** / **`images`**: Visual assets for the event

## 🔑 API Key Setup

This actor requires a **free** Ticketmaster Discovery API key:

1. Go to [developer.ticketmaster.com](https://developer.ticketmaster.com/)
2. Create a free account
3. Copy your **Consumer Key** from the dashboard — that's your API key

Rate limits: **5,000 calls/day** and **5 requests/second**. More than enough for typical use.

## 💰 Pricing

This Actor uses a **pay-per-event** pricing model at **$0.0005 per result** (that's $0.50 per 1,000 events).

Free tier users get **25 results per run** at no cost.

## 🎯 Use Cases

- **Price Monitoring**: Track ticket price ranges for specific events, artists, or venues over time
- **Event Discovery**: Find upcoming concerts, sports games, theater shows, and festivals in any city or region
- **Market Research**: Analyze event pricing trends across venues, genres, regions, or time periods
- **Presale Alerting**: Monitor presale dates and on-sale windows for high-demand events
- **Venue Intelligence**: Research venue details, locations, and upcoming event counts
- **Travel Planning**: Build event-aware travel recommendation systems
- **AI Agents**: Feed real-time event and ticket data into LLM pipelines via MCP integration

## 🤖 MCP Integration

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

## 📝 Notes

- Uses the **official Ticketmaster Discovery API** — no browser, no Playwright, no bot detection issues
- Ticketmaster limits deep pagination to **~1,000 results per search query**. Use filters to narrow results
- Price data is **min/max ranges**, not individual seat prices. Real-time seat-level availability is not provided
- Best geographic coverage for **US, Canada, UK, Mexico**, and select European markets
- All dates must be in **ISO 8601 format with timezone** (e.g. `2025-06-01T00:00:00Z`)
- Results are automatically deduplicated by event ID within a single run
- The actor supports **Apify state persistence** for resumable long-running searches

**Made with ❤️ for event data enthusiasts**

*Transform your event intelligence with the most reliable Ticketmaster scraper on Apify.*
