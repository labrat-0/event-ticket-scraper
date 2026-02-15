"""
Core Ticketmaster Discovery API client.

Handles event search, event lookup by ID, and venue search
with rate limiting, pagination, and retry on 429.

API docs: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import AsyncGenerator

import httpx

from .models import EventRecord, PresaleRecord, ScraperInput, VenueRecord

logger = logging.getLogger("src")

# ---------------------------------------------------------------------------
# Ticketmaster Discovery API
# ---------------------------------------------------------------------------

_TM_BASE = "https://app.ticketmaster.com/discovery/v2"
_TM_PAGE_SIZE = 200  # max allowed by the API
_TM_DEEP_PAGE_LIMIT = 1000  # size * page must be < 1000


class RateLimiter:
    """Async rate limiter ensuring minimum interval between requests."""

    def __init__(self, interval_secs: float = 0.5) -> None:
        self._interval = interval_secs
        self._lock = asyncio.Lock()
        self._last_request: float = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = asyncio.get_running_loop().time()
            elapsed = now - self._last_request
            if elapsed < self._interval:
                await asyncio.sleep(self._interval - elapsed)
            self._last_request = asyncio.get_running_loop().time()


class EventTicketScraper:
    """Searches and retrieves events from the Ticketmaster Discovery API."""

    _MAX_RETRIES = 3
    _BACKOFF_SECS = (5.0, 15.0, 30.0)
    _USER_AGENT = (
        "EventTicketScraper/1.0 (Apify Actor; "
        "https://apify.com/labrat011/event-ticket-scraper)"
    )

    def __init__(
        self,
        config: ScraperInput,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._config = config
        self._client = http_client
        self._rate_limiter = RateLimiter(config.request_interval_secs)

    async def _api_request(
        self,
        endpoint: str,
        params: dict[str, str | int] | None = None,
    ) -> httpx.Response | None:
        """Make a Ticketmaster API request with retry + backoff on 429.

        Returns the Response on success, or None if all retries exhausted
        or a non-retryable error occurs.
        """
        if params is None:
            params = {}
        params["apikey"] = self._config.api_key

        url = f"{_TM_BASE}/{endpoint}"

        for attempt in range(self._MAX_RETRIES + 1):
            await self._rate_limiter.wait()
            try:
                resp = await self._client.get(
                    url,
                    params=params,
                    timeout=30,
                    headers={"User-Agent": self._USER_AGENT},
                )
            except httpx.HTTPError as exc:
                logger.error("Ticketmaster request failed: %s", exc)
                return None

            if resp.status_code == 401:
                logger.error(
                    "Ticketmaster API returned 401 Unauthorized. "
                    "Check that your API key is valid."
                )
                return None

            if resp.status_code == 400:
                logger.error(
                    "Ticketmaster API returned 400 Bad Request: %s",
                    resp.text[:500],
                )
                return None

            if resp.status_code != 429:
                return resp

            # 429 -- rate limited
            if attempt >= self._MAX_RETRIES:
                logger.error(
                    "Ticketmaster rate limited after %d retries, giving up.",
                    self._MAX_RETRIES,
                )
                return None

            retry_after = resp.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_secs = float(retry_after)
                except ValueError:
                    wait_secs = self._BACKOFF_SECS[attempt]
            else:
                wait_secs = self._BACKOFF_SECS[attempt]

            logger.warning(
                "Ticketmaster rate limited (429), retry %d/%d in %.1fs",
                attempt + 1,
                self._MAX_RETRIES,
                wait_secs,
            )
            await asyncio.sleep(wait_secs)

        return None

    async def run(self) -> AsyncGenerator[dict, None]:
        """Execute the configured mode and yield records."""
        mode = self._config.mode

        if mode == "search":
            async for record in self._search_events():
                yield record
        elif mode == "get_event":
            async for record in self._get_event():
                yield record
        elif mode == "venues":
            async for record in self._search_venues():
                yield record
        else:
            logger.error("Unknown mode: %s", mode)

    # ------------------------------------------------------------------
    # Event Search
    # ------------------------------------------------------------------

    async def _search_events(self) -> AsyncGenerator[dict, None]:
        """Search events via Ticketmaster Discovery API."""
        config = self._config
        max_results = config.max_results
        total_yielded = 0
        page = 0

        logger.info(
            "Searching events: keyword='%s', city='%s', state='%s', "
            "country='%s', classification='%s'",
            config.keyword,
            config.city,
            config.state_code,
            config.country_code,
            config.classification_name,
        )

        while total_yielded < max_results:
            # Calculate page size: can't exceed deep paging limit
            remaining = max_results - total_yielded
            page_size = min(_TM_PAGE_SIZE, remaining)

            # Deep paging guard: size * page must be < 1000
            if page_size * page >= _TM_DEEP_PAGE_LIMIT:
                logger.info(
                    "Reached Ticketmaster deep paging limit (%d). "
                    "Try narrowing your search with filters.",
                    _TM_DEEP_PAGE_LIMIT,
                )
                break

            params: dict[str, str | int] = {
                "size": page_size,
                "page": page,
            }

            # Add search filters
            if config.keyword.strip():
                params["keyword"] = config.keyword.strip()
            if config.city.strip():
                params["city"] = config.city.strip()
            if config.state_code.strip():
                params["stateCode"] = config.state_code.strip()
            if config.country_code.strip():
                params["countryCode"] = config.country_code.strip()
            if config.postal_code.strip():
                params["postalCode"] = config.postal_code.strip()
            if config.latlong.strip():
                params["latlong"] = config.latlong.strip()
            if config.radius is not None:
                params["radius"] = config.radius
                params["unit"] = config.unit
            if config.classification_name.strip():
                params["classificationName"] = config.classification_name.strip()
            if config.start_date_time.strip():
                params["startDateTime"] = config.start_date_time.strip()
            if config.end_date_time.strip():
                params["endDateTime"] = config.end_date_time.strip()
            if config.sort.strip():
                params["sort"] = config.sort.strip()
            if config.source.strip():
                params["source"] = config.source.strip()
            if config.include_family.strip():
                params["includeFamily"] = config.include_family.strip()

            resp = await self._api_request("events.json", params)
            if resp is None:
                return

            if resp.status_code != 200:
                logger.error(
                    "Event search returned %d: %s",
                    resp.status_code,
                    resp.text[:500],
                )
                return

            data = resp.json()

            # Check if there are any results
            embedded = data.get("_embedded")
            if not embedded or "events" not in embedded:
                if page == 0:
                    logger.info("No events found matching your search criteria.")
                break

            events = embedded["events"]
            page_info = data.get("page", {})
            total_elements = page_info.get("totalElements", 0)

            logger.info(
                "Event search page %d: got %d events (total available: %d)",
                page,
                len(events),
                total_elements,
            )

            for event_data in events:
                if total_yielded >= max_results:
                    return

                record = _event_to_record(event_data)
                yield record.model_dump()
                total_yielded += 1

            page += 1

            # No more pages
            total_pages = page_info.get("totalPages", 0)
            if page >= total_pages:
                break

        logger.info("Event search complete: %d events yielded", total_yielded)

    # ------------------------------------------------------------------
    # Get Event by ID
    # ------------------------------------------------------------------

    async def _get_event(self) -> AsyncGenerator[dict, None]:
        """Look up a single event by Ticketmaster event ID."""
        event_id = self._config.event_id.strip()
        logger.info("Looking up event: %s", event_id)

        resp = await self._api_request(f"events/{event_id}.json")
        if resp is None:
            return

        if resp.status_code == 404:
            logger.warning("Event not found: %s", event_id)
            yield EventRecord(
                event_name=f"Event not found: {event_id}",
                event_id=event_id,
                scraped_at=_now_iso(),
            ).model_dump()
            return

        if resp.status_code != 200:
            logger.error(
                "Event lookup returned %d: %s",
                resp.status_code,
                resp.text[:500],
            )
            return

        event_data = resp.json()
        record = _event_to_record(event_data)
        yield record.model_dump()

    # ------------------------------------------------------------------
    # Venue Search
    # ------------------------------------------------------------------

    async def _search_venues(self) -> AsyncGenerator[dict, None]:
        """Search venues via Ticketmaster Discovery API."""
        config = self._config
        max_results = config.max_results
        total_yielded = 0
        page = 0

        logger.info(
            "Searching venues: keyword='%s', city='%s', state='%s', country='%s'",
            config.keyword,
            config.city,
            config.state_code,
            config.country_code,
        )

        while total_yielded < max_results:
            remaining = max_results - total_yielded
            page_size = min(_TM_PAGE_SIZE, remaining)

            if page_size * page >= _TM_DEEP_PAGE_LIMIT:
                logger.info("Reached Ticketmaster deep paging limit for venues.")
                break

            params: dict[str, str | int] = {
                "size": page_size,
                "page": page,
            }

            if config.keyword.strip():
                params["keyword"] = config.keyword.strip()
            if config.city.strip():
                params["city"] = config.city.strip()
            if config.state_code.strip():
                params["stateCode"] = config.state_code.strip()
            if config.country_code.strip():
                params["countryCode"] = config.country_code.strip()
            if config.postal_code.strip():
                params["postalCode"] = config.postal_code.strip()
            if config.latlong.strip():
                params["latlong"] = config.latlong.strip()
            if config.radius is not None:
                params["radius"] = config.radius
                params["unit"] = config.unit

            resp = await self._api_request("venues.json", params)
            if resp is None:
                return

            if resp.status_code != 200:
                logger.error(
                    "Venue search returned %d: %s",
                    resp.status_code,
                    resp.text[:500],
                )
                return

            data = resp.json()
            embedded = data.get("_embedded")
            if not embedded or "venues" not in embedded:
                if page == 0:
                    logger.info("No venues found matching your search criteria.")
                break

            venues = embedded["venues"]
            page_info = data.get("page", {})
            total_elements = page_info.get("totalElements", 0)

            logger.info(
                "Venue search page %d: got %d venues (total available: %d)",
                page,
                len(venues),
                total_elements,
            )

            for venue_data in venues:
                if total_yielded >= max_results:
                    return

                record = _venue_to_record(venue_data)
                yield record.model_dump()
                total_yielded += 1

            page += 1
            total_pages = page_info.get("totalPages", 0)
            if page >= total_pages:
                break

        logger.info("Venue search complete: %d venues yielded", total_yielded)


# ---------------------------------------------------------------------------
# Event response -> EventRecord
# ---------------------------------------------------------------------------


def _event_to_record(event: dict) -> EventRecord:
    """Convert a Ticketmaster event API object to an EventRecord."""
    # Dates
    dates = event.get("dates", {})
    start = dates.get("start", {})
    status_data = dates.get("status", {})

    # Price ranges
    price_ranges = event.get("priceRanges", [])
    price_min = 0.0
    price_max = 0.0
    price_currency = ""
    if price_ranges:
        # Use the first price range (typically "standard")
        pr = price_ranges[0]
        price_min = pr.get("min", 0.0) or 0.0
        price_max = pr.get("max", 0.0) or 0.0
        price_currency = pr.get("currency", "") or ""

    # Venue (from _embedded)
    embedded = event.get("_embedded", {})
    venues = embedded.get("venues", [])
    venue = venues[0] if venues else {}
    venue_loc = venue.get("location", {})

    # Attractions
    attractions_data = embedded.get("attractions", [])
    attraction_names = [
        a.get("name", "") for a in attractions_data if a.get("name")
    ]

    # Classifications
    classifications = event.get("classifications", [])
    segment = ""
    genre = ""
    sub_genre = ""
    if classifications:
        cls0 = classifications[0]
        seg = cls0.get("segment", {})
        gen = cls0.get("genre", {})
        sub = cls0.get("subGenre", {})
        segment = seg.get("name", "") or ""
        genre = gen.get("name", "") or ""
        sub_genre = sub.get("name", "") or ""
        # "Undefined" is a common placeholder in the API
        if segment == "Undefined":
            segment = ""
        if genre == "Undefined":
            genre = ""
        if sub_genre == "Undefined":
            sub_genre = ""

    # Sales
    sales = event.get("sales", {})
    public_sale = sales.get("public", {})
    presales_data = sales.get("presales", [])
    presales: list[dict] = []
    for ps in presales_data:
        presale = PresaleRecord(
            name=ps.get("name", "") or "",
            start_date_time=ps.get("startDateTime", "") or "",
            end_date_time=ps.get("endDateTime", "") or "",
            description=ps.get("description", "") or "",
            url=ps.get("url", "") or "",
        )
        presales.append(presale.model_dump())

    # Promoter
    promoter_data = event.get("promoter", {})
    promoter_name = promoter_data.get("name", "") or ""

    # Seatmap
    seatmap = event.get("seatmap", {})

    # Images -- pick unique URLs (highest resolution of each ratio)
    images_data = event.get("images", [])
    image_urls: list[str] = []
    seen_ratios: set[str] = set()
    # Sort by width descending to get highest res first
    sorted_images = sorted(
        images_data, key=lambda i: i.get("width", 0), reverse=True
    )
    for img in sorted_images:
        ratio = img.get("ratio", "")
        url = img.get("url", "")
        if url and ratio not in seen_ratios:
            seen_ratios.add(ratio)
            image_urls.append(url)

    # Venue details
    venue_address_obj = venue.get("address", {})
    venue_city_obj = venue.get("city", {})
    venue_state_obj = venue.get("state", {})
    venue_country_obj = venue.get("country", {})

    return EventRecord(
        event_name=event.get("name", "") or "",
        event_id=event.get("id", "") or "",
        event_url=event.get("url", "") or "",
        local_date=start.get("localDate", "") or "",
        local_time=start.get("localTime", "") or "",
        datetime_utc=start.get("dateTime", "") or "",
        timezone=dates.get("timezone", "") or "",
        status=status_data.get("code", "") or "",
        price_min=price_min,
        price_max=price_max,
        price_currency=price_currency,
        venue_name=venue.get("name", "") or "",
        venue_id=venue.get("id", "") or "",
        venue_city=venue_city_obj.get("name", "") or "",
        venue_state=venue_state_obj.get("name", "") or "",
        venue_country=venue_country_obj.get("name", "") or "",
        venue_address=venue_address_obj.get("line1", "") or "",
        venue_postal_code=venue.get("postalCode", "") or "",
        venue_latitude=_safe_float(venue_loc.get("latitude")),
        venue_longitude=_safe_float(venue_loc.get("longitude")),
        attractions=attraction_names,
        segment=segment,
        genre=genre,
        sub_genre=sub_genre,
        public_sale_start=public_sale.get("startDateTime", "") or "",
        public_sale_end=public_sale.get("endDateTime", "") or "",
        presales=presales,
        promoter=promoter_name,
        seatmap_url=seatmap.get("staticUrl", "") or "",
        images=image_urls,
        info=event.get("info", "") or "",
        please_note=event.get("pleaseNote", "") or "",
        ticket_limit=(event.get("ticketLimit", {}) or {}).get("info", "") or "",
        accessibility_info=(event.get("accessibility", {}) or {}).get("info", "") or "",
        source="ticketmaster",
        scraped_at=_now_iso(),
    )


# ---------------------------------------------------------------------------
# Venue response -> VenueRecord
# ---------------------------------------------------------------------------


def _venue_to_record(venue: dict) -> VenueRecord:
    """Convert a Ticketmaster venue API object to a VenueRecord."""
    location = venue.get("location", {})
    address = venue.get("address", {})
    city_obj = venue.get("city", {})
    state_obj = venue.get("state", {})
    country_obj = venue.get("country", {})
    general_info = venue.get("generalInfo", {})

    # Images
    images_data = venue.get("images", [])
    image_urls = [img.get("url", "") for img in images_data if img.get("url")]

    # Upcoming events count
    upcoming = venue.get("upcomingEvents", {})
    upcoming_count = upcoming.get("_total", 0) if isinstance(upcoming, dict) else 0

    return VenueRecord(
        venue_name=venue.get("name", "") or "",
        venue_id=venue.get("id", "") or "",
        venue_url=venue.get("url", "") or "",
        city=city_obj.get("name", "") or "",
        state=state_obj.get("name", "") or "",
        country=country_obj.get("name", "") or "",
        address=address.get("line1", "") or "",
        postal_code=venue.get("postalCode", "") or "",
        latitude=_safe_float(location.get("latitude")),
        longitude=_safe_float(location.get("longitude")),
        timezone=venue.get("timezone", "") or "",
        parking_detail=general_info.get("parkingDetail", "") or "",
        general_info=general_info.get("generalRule", "") or "",
        child_rule=general_info.get("childRule", "") or "",
        accessible_seating_detail=venue.get("accessibleSeatingDetail", "") or "",
        upcoming_events_count=upcoming_count,
        images=image_urls,
        source="ticketmaster",
        scraped_at=_now_iso(),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(value: str | float | None) -> float:
    """Safely convert a value to float, returning 0.0 on failure."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
