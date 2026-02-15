"""
Pydantic models for Event Ticket Scraper input and output.

All output fields have defaults -- no missing keys in output.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScraperInput(BaseModel):
    """Validated scraper configuration parsed from actor input."""

    api_key: str = ""
    mode: str = "search"  # search, get_event, venues

    # Search parameters
    keyword: str = ""
    event_id: str = ""

    # Location filters
    city: str = ""
    state_code: str = ""
    country_code: str = ""
    postal_code: str = ""
    latlong: str = ""
    radius: int | None = None
    unit: str = "miles"

    # Event filters
    classification_name: str = ""
    start_date_time: str = ""
    end_date_time: str = ""
    sort: str = "relevance,desc"
    source: str = ""
    include_family: str = ""

    # Output settings
    max_results: int = Field(default=100, ge=1, le=1000)

    # Advanced
    request_interval_secs: float = Field(default=0.5, ge=0.2, le=5.0)

    @classmethod
    def from_actor_input(cls, raw: dict[str, Any]) -> ScraperInput:
        """Map camelCase actor input keys to snake_case model fields."""
        return cls(
            api_key=raw.get("apiKey", ""),
            mode=raw.get("mode", "search"),
            keyword=raw.get("keyword", ""),
            event_id=raw.get("eventId", ""),
            city=raw.get("city", ""),
            state_code=raw.get("stateCode", ""),
            country_code=raw.get("countryCode", ""),
            postal_code=raw.get("postalCode", ""),
            latlong=raw.get("latlong", ""),
            radius=raw.get("radius"),
            unit=raw.get("unit", "miles"),
            classification_name=raw.get("classificationName", ""),
            start_date_time=raw.get("startDateTime", ""),
            end_date_time=raw.get("endDateTime", ""),
            sort=raw.get("sort", "relevance,desc"),
            source=raw.get("source", ""),
            include_family=raw.get("includeFamily", ""),
            max_results=raw.get("maxResults", 100),
            request_interval_secs=raw.get("requestIntervalSecs", 0.5),
        )

    def validate_input(self) -> str | None:
        """Return error string if input is invalid, else None."""
        if not self.api_key.strip():
            return (
                "Ticketmaster API key is required. "
                "Get one for free at https://developer.ticketmaster.com/"
            )

        if self.mode not in ("search", "get_event", "venues"):
            return f"Invalid mode: '{self.mode}'. Use 'search', 'get_event', or 'venues'."

        if self.mode == "get_event" and not self.event_id.strip():
            return "Event ID is required for 'get_event' mode."

        if self.mode == "search" and not any([
            self.keyword.strip(),
            self.city.strip(),
            self.state_code.strip(),
            self.country_code.strip(),
            self.postal_code.strip(),
            self.latlong.strip(),
            self.classification_name.strip(),
        ]):
            return (
                "Provide at least one search filter: keyword, city, stateCode, "
                "countryCode, postalCode, latlong, or classificationName."
            )

        if self.unit not in ("miles", "km"):
            return f"Invalid unit: '{self.unit}'. Use 'miles' or 'km'."

        return None


class PresaleRecord(BaseModel):
    """A presale window for an event."""

    name: str = ""
    start_date_time: str = ""
    end_date_time: str = ""
    description: str = ""
    url: str = ""


class EventRecord(BaseModel):
    """One event from Ticketmaster.

    Every field has a default -- output never has missing keys.
    """

    schema_version: str = "1.0"
    type: str = "event"

    # Core event info
    event_name: str = ""
    event_id: str = ""
    event_url: str = ""

    # Date and time
    local_date: str = ""  # YYYY-MM-DD
    local_time: str = ""  # HH:MM:SS
    datetime_utc: str = ""  # ISO 8601 with timezone
    timezone: str = ""

    # Status
    status: str = ""  # onsale, offsale, canceled, postponed, rescheduled

    # Pricing
    price_min: float = 0.0
    price_max: float = 0.0
    price_currency: str = ""

    # Venue
    venue_name: str = ""
    venue_id: str = ""
    venue_city: str = ""
    venue_state: str = ""
    venue_country: str = ""
    venue_address: str = ""
    venue_postal_code: str = ""
    venue_latitude: float = 0.0
    venue_longitude: float = 0.0

    # Attractions (artists, teams, etc.)
    attractions: list[str] = Field(default_factory=list)

    # Classification
    segment: str = ""  # e.g. Music, Sports, Arts & Theatre
    genre: str = ""  # e.g. Rock, Pop, NBA
    sub_genre: str = ""  # e.g. Alternative Rock, Pop Rock

    # Sales info
    public_sale_start: str = ""
    public_sale_end: str = ""
    presales: list[dict] = Field(default_factory=list)

    # Promoter
    promoter: str = ""

    # Media
    seatmap_url: str = ""
    images: list[str] = Field(default_factory=list)

    # Additional info
    info: str = ""
    please_note: str = ""
    ticket_limit: str = ""
    accessibility_info: str = ""

    # Metadata
    source: str = "ticketmaster"
    scraped_at: str = ""


class VenueRecord(BaseModel):
    """One venue from Ticketmaster.

    Every field has a default -- output never has missing keys.
    """

    schema_version: str = "1.0"
    type: str = "venue"

    # Core venue info
    venue_name: str = ""
    venue_id: str = ""
    venue_url: str = ""

    # Location
    city: str = ""
    state: str = ""
    country: str = ""
    address: str = ""
    postal_code: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = ""

    # Details
    parking_detail: str = ""
    general_info: str = ""
    child_rule: str = ""
    accessible_seating_detail: str = ""
    upcoming_events_count: int = 0

    # Media
    images: list[str] = Field(default_factory=list)

    # Metadata
    source: str = "ticketmaster"
    scraped_at: str = ""
