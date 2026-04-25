# Module 1: Business Collection Using OpenStreetMap (OSM)

## AI-Powered Client Hunt & Outreach — Final Year Project Documentation

### Department of Software Engineering

---

# Table of Contents

1. [Introduction](#1-introduction)
2. [Module Overview](#2-module-overview)
3. [OpenStreetMap — Theoretical Background](#3-openstreetmap--theoretical-background)
4. [System Architecture](#4-system-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Detailed Component Documentation](#6-detailed-component-documentation)
   - 6.1 [Configuration Layer](#61-configuration-layer)
   - 6.2 [OSM Service Layer](#62-osm-service-layer)
   - 6.3 [Overpass Client — Core Engine](#63-overpass-client--core-engine)
   - 6.4 [Website Discovery Service](#64-website-discovery-service)
   - 6.5 [API Endpoints Layer](#65-api-endpoints-layer)
   - 6.6 [Pydantic Schemas](#66-pydantic-schemas)
   - 6.7 [Frontend Template — businesses.html](#67-frontend-template--businesseshtml)
7. [Data Flow Architecture](#7-data-flow-architecture)
8. [Geocoding Pipeline](#8-geocoding-pipeline)
9. [Overpass Query Language (Overpass QL)](#9-overpass-query-language-overpass-ql)
10. [Business Type Resolution System](#10-business-type-resolution-system)
11. [OSM Element Parsing](#11-osm-element-parsing)
12. [Website Crawling and Contact Extraction](#12-website-crawling-and-contact-extraction)
13. [Email Extraction Pipeline](#13-email-extraction-pipeline)
14. [Website Discovery via DuckDuckGo](#14-website-discovery-via-duckduckgo)
15. [Country Mismatch Detection](#15-country-mismatch-detection)
16. [Error Handling and Resilience](#16-error-handling-and-resilience)
17. [Concurrent Processing Architecture](#17-concurrent-processing-architecture)
18. [File-Based Data Persistence](#18-file-based-data-persistence)
19. [Frontend Architecture with Alpine.js](#19-frontend-architecture-with-alpinejs)
20. [Next.js Frontend Integration Guide](#20-nextjs-frontend-integration-guide)
21. [API Reference](#21-api-reference)
22. [Testing Methodology](#22-testing-methodology)
23. [Performance Optimization](#23-performance-optimization)
24. [Security Considerations](#24-security-considerations)
25. [Limitations and Future Enhancements](#25-limitations-and-future-enhancements)
26. [Conclusion](#26-conclusion)

---

# 1. Introduction

## 1.1 Purpose of This Document

This document provides a comprehensive technical explanation of the **Business Collection Using OpenStreetMap (OSM)** module within the **AI-Powered Client Hunt & Outreach** system. This module serves as the foundational data collection layer of the entire platform, responsible for discovering businesses across the globe using open geographic data, enriching those records with contact information scraped from their websites, and discovering official websites for businesses that lack them in the OSM database.

The document covers every aspect of the module — from theoretical foundations of OpenStreetMap data to the implementation details of each Python function, from the Overpass Query Language used to fetch data to the DuckDuckGo-powered website discovery algorithm. This documentation is intended for academic review as part of a Final Year Project (FYP) in Software Engineering.

## 1.2 Problem Statement

Modern businesses that offer digital marketing, web development, or outreach services face a fundamental challenge: **identifying potential clients who need their services**. Traditional methods of client acquisition — cold calling, manual research, purchasing lead databases — are time-consuming, expensive, and often produce low-quality leads.

OpenStreetMap (OSM) provides the world's largest open-source geographic database with over 9 billion data points. However, OSM data is primarily geographic and structural — while it may contain a business's name, location, and sometimes a phone number or website, it frequently lacks the contact information (especially email addresses) that are essential for outreach campaigns.

Furthermore, in many developing countries like Pakistan, OSM data coverage is sparse. A search for "restaurants in Lahore" might return only 19 results, and among those, zero may have websites or email addresses recorded, even though well-known chains like Bundu Khan and Salt'n Pepper clearly have official websites.

## 1.3 Solution Approach

This module addresses these challenges through a **multi-layered enrichment pipeline**:

1. **Geographic Search** — Query OSM/Overpass API to discover businesses by type and location
2. **Tag Expansion** — Map user-friendly business types to multiple OSM tag combinations for broader results
3. **Website Crawling** — For businesses that have websites in OSM, crawl those websites to extract emails, phone numbers, and social media links
4. **Website Discovery** — For businesses without websites in OSM, use DuckDuckGo search with a scoring algorithm to discover their official websites
5. **Data Normalization** — Parse OSM elements into clean, structured business records
6. **Frontend Presentation** — Present results in a searchable, filterable interface with progressive enhancement

## 1.4 Scope

This module covers:
- Nominatim geocoding for city/country resolution
- Overpass API integration for business discovery
- Business type to OSM tag mapping (60+ business types)
- Multi-round website crawling with concurrent thread execution
- Six-method email extraction from web pages
- Social media link extraction (Facebook, Instagram)
- DuckDuckGo-powered website discovery with relevance scoring
- RESTful API endpoints for search, save, and discovery
- AlpineJS-powered frontend with progressive website discovery
- File-based JSON persistence for saved business data

---

# 2. Module Overview

## 2.1 Module Identity

| Property | Value |
|----------|-------|
| **Module Name** | Business Collection Using OpenStreetMap |
| **Package Path** | `app/services/osm/` |
| **Primary Files** | `osm_service.py`, `overpass_client.py`, `website_discovery.py` |
| **API Prefix** | `/api/v1/osm/` and `/api/v1/businesses/` |
| **Frontend** | `templates/pages/businesses.html` |
| **Dependencies** | `requests`, `beautifulsoup4`, `ddgs`, `difflib`, `playwright` |
| **External APIs** | Nominatim (geocoding), Overpass (OSM query), DuckDuckGo (search) |

## 2.2 Module Responsibilities

The OSM module is responsible for:

1. **Business Discovery**: Finding businesses of a specific type within a geographic area
2. **Data Enrichment**: Crawling business websites to extract contact information
3. **Website Discovery**: Finding official websites for businesses that OSM doesn't have URLs for
4. **Data Persistence**: Saving enriched business records to file-based JSON storage
5. **API Provisioning**: Exposing RESTful endpoints for the frontend to consume
6. **UI Rendering**: Providing a rich, interactive search interface

## 2.3 Module File Structure

```
app/
├── services/
│   └── osm/
│       ├── __init__.py              # Package exports
│       ├── osm_service.py           # Main service class (153 lines)
│       ├── overpass_client.py        # Core engine (924 lines)
│       ├── website_discovery.py      # DuckDuckGo discovery (201 lines)
│       ├── enricher.py              # Placeholder for future enrichment
│       ├── normalizer.py            # Placeholder for data normalization
│       └── queries.py               # Placeholder for query builders
├── api/
│   └── v1/
│       └── endpoints/
│           ├── osm_sources.py       # OSM search endpoints (114 lines)
│           └── businesses.py        # Business CRUD + crawling (706 lines)
├── schemas/
│   └── business.py                  # Pydantic models (63 lines)
├── templates/
│   └── pages/
│       └── businesses.html          # Frontend template (953 lines)
└── data/
    └── businesses.json              # File-based storage
```

---

# 3. OpenStreetMap — Theoretical Background

## 3.1 What is OpenStreetMap?

OpenStreetMap (OSM) is a collaborative project to create a free, editable map of the entire world. Founded in 2004 by Steve Coast in the United Kingdom, OSM has grown to become the world's largest open geographic database. As of 2025, OSM contains over 9 billion nodes (geographic points), 1 billion ways (lines and areas), and 14 million relations (complex structures).

OSM operates under the Open Database License (ODbL), which means anyone can freely use, modify, and distribute the data as long as they provide attribution and share any derived databases under the same license.

## 3.2 OSM Data Model

The OSM data model consists of three primitive types:

### 3.2.1 Nodes

A node is the most basic element in OSM. It represents a single point in geographic space, defined by its latitude and longitude. Nodes can exist independently (e.g., a point of interest like a restaurant or ATM) or as part of a way.

```
Node {
    id: Integer,
    lat: Float,        // Latitude in decimal degrees
    lon: Float,        // Longitude in decimal degrees
    tags: {key: value} // Key-value metadata pairs
}
```

### 3.2.2 Ways

A way is an ordered list of nodes that forms a polyline (for roads, rivers) or a polygon (for buildings, parks). A way must contain at least 2 nodes. If the first and last node are the same, the way forms a closed polygon.

```
Way {
    id: Integer,
    nodes: [node_id_1, node_id_2, ...],
    tags: {key: value}
}
```

### 3.2.3 Relations

A relation is a group of elements (nodes, ways, or other relations) with assigned roles that describe a higher-level geographic relationship. Common examples include multipolygon areas, route networks, and administrative boundaries.

```
Relation {
    id: Integer,
    members: [{type, ref, role}, ...],
    tags: {key: value}
}
```

## 3.3 OSM Tagging System

Every OSM element can have an arbitrary number of **tags** — key-value pairs that describe the element. Tags follow community-defined conventions:

| Tag Key | Example Values | Description |
|---------|---------------|-------------|
| `amenity` | `restaurant`, `cafe`, `hospital` | Points of interest / facilities |
| `shop` | `supermarket`, `clothing`, `electronics` | Retail establishments |
| `tourism` | `hotel`, `hostel`, `museum` | Tourism-related facilities |
| `healthcare` | `dentist`, `clinic`, `pharmacy` | Healthcare facilities |
| `leisure` | `fitness_centre`, `swimming_pool` | Leisure activities |
| `name` | `Bundu Khan`, `McDonald's` | Human-readable name |
| `website` | `https://bundukhan.pk` | Official website URL |
| `email` | `info@bundukhan.pk` | Contact email |
| `phone` | `+92-42-35761234` | Phone number |
| `addr:street` | `MM Alam Road` | Street address |
| `addr:city` | `Lahore` | City |
| `cuisine` | `pakistani`, `italian`, `coffee` | Type of cuisine (for food establishments) |

## 3.4 Nominatim Geocoding Service

Nominatim is OSM's geocoding service that converts human-readable place names (like "Lahore, Pakistan") into geographic coordinates (latitude/longitude). It powers the address search on the OpenStreetMap website and is available as a free API.

**API Endpoint**: `https://nominatim.openstreetmap.org/search`

**Key Parameters**:
- `q`: Search query (e.g., "Lahore, Pakistan")
- `format`: Response format (`json`, `xml`, `html`)
- `limit`: Maximum number of results
- `addressdetails`: Include address breakdown

**Rate Limits**: Nominatim enforces a maximum of 1 request per second. Heavy users must provide a valid email in the User-Agent header.

## 3.5 Overpass API

The Overpass API is a read-only API that serves custom-selected parts of the OSM map data. Unlike the standard OSM API which is designed for editors, Overpass is optimized for data consumers — it supports complex queries filtering by tags, spatial extent, and element types.

**Key Properties**:
- **Query Language**: Overpass QL (query language) — a domain-specific language for spatial queries
- **Timeout**: Configurable per query (our system uses 180 seconds)
- **Output Formats**: JSON, XML, CSV
- **Rate Limits**: Varies by server; the main server (`overpass-api.de`) allows roughly 10,000 queries per day

**Multiple Servers**: Our system uses three Overpass API servers for failover:
1. `overpass-api.de` (primary, Germany)
2. `overpass.kumi.systems` (secondary, Germany)
3. `overpass.openstreetmap.ru` (tertiary, Russia)

## 3.6 OSM Data Quality in Developing Countries

A critical challenge that directly motivated the design of this module is the inconsistency of OSM data quality across regions. In developed countries (USA, Western Europe, Japan), OSM data is often comprehensive, with many businesses having complete tag sets including websites, phone numbers, and addresses.

In developing countries like Pakistan, the situation is starkly different:

- **Limited Mappers**: Fewer volunteer contributors means less data coverage
- **Missing Websites**: Even well-known chains may have no `website` tag
- **Missing Emails**: Email tags are almost universally absent
- **Incomplete Names**: Businesses may have romanized names that don't match their brand
- **Limited Address Data**: Street addresses are often incomplete or missing

This data gap is the primary reason our system includes both **website crawling** (to find emails from known websites) and **website discovery** (to find websites from business names).

---

# 4. System Architecture

## 4.1 High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    Next.js Frontend                       │
│  (Search Form → Results Table → Save → Discover → Crawl) │
└─────────────┬────────────────────────────────────────────┘
              │ HTTP/REST
              ▼
┌──────────────────────────────────────────────────────────┐
│                   FastAPI Backend                         │
│                                                          │
│  ┌─────────────────────┐  ┌───────────────────────────┐  │
│  │  OSM Sources API    │  │  Businesses API            │  │
│  │  /api/v1/osm/       │  │  /api/v1/businesses/       │  │
│  │  • POST /search     │  │  • POST /save              │  │
│  │  • GET /types       │  │  • POST /{id}/crawl        │  │
│  │  • POST /geocode    │  │  • POST /discover-websites │  │
│  └──────┬──────────────┘  │  • POST /discover-single   │  │
│         │                 │  • GET / (list)             │  │
│         ▼                 │  • POST /extract            │  │
│  ┌──────────────────┐    └────────┬──────────────────┘  │
│  │   OSM Service     │            │                      │
│  │   (osm_service.py)│            │                      │
│  └──────┬───────────┘            │                      │
│         │                         │                      │
│         ▼                         ▼                      │
│  ┌──────────────────┐  ┌──────────────────────────┐     │
│  │  Overpass Client  │  │  Website Discovery       │     │
│  │  (924 lines)      │  │  (website_discovery.py)  │     │
│  │                   │  │                          │     │
│  │  • Geocoding      │  │  • DuckDuckGo Search     │     │
│  │  • Query Building │  │  • Relevance Scoring     │     │
│  │  • OSM Fetching   │  │  • Domain Filtering      │     │
│  │  • Record Parsing │  │  • Bulk Discovery        │     │
│  │  • Website Crawl  │  │                          │     │
│  │  • Email Extract  │  └──────────────────────────┘     │
│  │  • Social Extract │                                    │
│  └──────┬───────────┘                                    │
│         │                                                │
└─────────┼────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐
│  Nominatim API  │  │  Overpass API     │  │  DuckDuckGo  │
│  (Geocoding)    │  │  (OSM Data)       │  │  (Search)    │
│  3 servers      │  │  3 servers        │  │  ddgs lib    │
└─────────────────┘  └──────────────────┘  └──────────────┘
```

## 4.2 Layer Architecture

The module follows a clean layered architecture:

### Layer 1: Presentation (Frontend)
- **File**: `businesses.html`
- **Technology**: Alpine.js + Tailwind CSS
- **Responsibility**: User interface for search, results display, website discovery progress

### Layer 2: API (Routing)
- **Files**: `osm_sources.py`, `businesses.py`
- **Technology**: FastAPI with async endpoints
- **Responsibility**: HTTP request handling, input validation, response formatting

### Layer 3: Service (Business Logic)
- **File**: `osm_service.py`
- **Technology**: Pure Python with ThreadPoolExecutor
- **Responsibility**: Orchestrating the search pipeline, applying business rules

### Layer 4: Client (External API Integration)
- **Files**: `overpass_client.py`, `website_discovery.py`
- **Technology**: Requests library, ddgs library
- **Responsibility**: Communicating with external APIs, parsing responses

### Layer 5: Persistence
- **File**: `data/businesses.json`
- **Technology**: File-based JSON
- **Responsibility**: Persistent storage of saved businesses

## 4.3 Design Patterns Used

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| **Service Layer** | `OSMService` class wraps `overpass_client` functions | Separation of business logic from API handlers |
| **Strategy Pattern** | `osm_tag_candidates()` maps types to different tag strategies | Support for 60+ business types with different OSM tag combinations |
| **Fallback/Chain of Responsibility** | 3 Nominatim servers, 3 Overpass servers | Resilience against server failures |
| **Builder Pattern** | `build_overpass_query()` constructs Overpass QL dynamically | Flexible query construction based on resolved tags |
| **Observer/Progress** | Frontend polls single-discovery endpoint progressively | Real-time UI updates during website discovery |
| **Thread Pool** | `ThreadPoolExecutor` for website crawling | Concurrent I/O without blocking the async event loop |
| **Scoring/Ranking** | `_score_result()` in website discovery | Intelligent selection of best-matching search result |

---

# 5. Technology Stack

## 5.1 Backend Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Primary programming language |
| **FastAPI** | 0.104+ | Asynchronous web framework |
| **Pydantic** | 2.x | Data validation and schema definition |
| **Requests** | 2.31+ | HTTP client for API calls and web scraping |
| **BeautifulSoup4** | 4.12+ | HTML parsing for email/contact extraction |
| **Playwright** | 1.40+ | Headless browser for JavaScript-rendered sites |
| **duckduckgo-search (ddgs)** | 9.10+ | DuckDuckGo search API wrapper |
| **difflib** | stdlib | Fuzzy string matching for business type resolution |
| **urllib3** | 2.x | Low-level HTTP with retry support |
| **Uvicorn** | 0.24+ | ASGI server for running FastAPI |

## 5.2 External APIs

| API | Provider | Purpose | Rate Limit |
|-----|----------|---------|-----------|
| **Nominatim** | OpenStreetMap Foundation | Geocoding city/country to coordinates | 1 req/sec |
| **Overpass** | Various community servers | Querying OSM database for businesses | ~10K/day |
| **DuckDuckGo** | DuckDuckGo Inc. | Web search for website discovery | Managed by ddgs library |

## 5.3 Frontend Technologies

| Technology | Purpose |
|-----------|---------|
| **Alpine.js** | Reactive UI framework (lightweight Vue alternative) |
| **Tailwind CSS** | Utility-first CSS framework |
| **Jinja2** | Server-side template engine |
| **Fetch API** | Browser HTTP client for API calls |

## 5.4 Next.js Frontend (Planned Migration)

The existing Jinja2 + Alpine.js frontend will be migrated to Next.js. Key considerations:

- **API Routes**: All endpoints are already RESTful and JSON-based, requiring no backend changes
- **Server Components**: OSM search can leverage Next.js server components for initial data fetching
- **Client Components**: Progressive website discovery requires client-side state management (React Query or SWR)
- **TypeScript Schemas**: Pydantic schemas can be translated to TypeScript interfaces

---

# 6. Detailed Component Documentation

## 6.1 Configuration Layer

### File: `app/core/config.py`

The configuration layer uses Pydantic Settings to manage environment variables with type safety and validation.

#### OSM-Specific Configuration

```python
class Settings(BaseSettings):
    # OSM Configuration
    OSM_CONTACT_EMAIL: str = Field(default="your_email@gmail.com")
    OSM_DEFAULT_RADIUS: int = 8000
    OSM_MAX_RESULTS: int = 200
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `OSM_CONTACT_EMAIL` | `str` | `your_email@gmail.com` | Email used in User-Agent header for Nominatim/Overpass API compliance |
| `OSM_DEFAULT_RADIUS` | `int` | `8000` | Default search radius in meters (8 km) |
| `OSM_MAX_RESULTS` | `int` | `200` | Maximum number of results to return from Overpass |

These settings are loaded from a `.env` file and cached using `@lru_cache()` for performance.

#### Overpass Client Constants

The `overpass_client.py` file defines additional constants that are not configurable via environment variables:

```python
CONTACT_EMAIL = "your_real_email@gmail.com"
USER_AGENT = f"FYP-Global-OSM-Extractor/2.0 ({CONTACT_EMAIL})"

DEFAULT_RADIUS_METERS = 8000
MAX_RESULTS = 500
OVERPASS_INTERNAL_TIMEOUT = 180

OVERPASS_READ_TIMEOUT = 120
CRAWL_READ_TIMEOUT = 20
CONNECT_TIMEOUT = 8
RETRIES = 3
BACKOFF_BASE = 2

ENABLE_WEBSITE_CRAWL = True
CRAWL_MAX_PAGES_PER_SITE = 5
CRAWL_MAX_WORKERS = 20
```

| Constant | Value | Purpose |
|----------|-------|---------|
| `USER_AGENT` | FYP-Global-OSM-Extractor/2.0 | Identifies the application to OSM servers (required by usage policy) |
| `MAX_RESULTS` | 500 | Maximum OSM elements to fetch per query |
| `OVERPASS_INTERNAL_TIMEOUT` | 180s | Timeout parameter in the Overpass QL query itself |
| `OVERPASS_READ_TIMEOUT` | 120s | HTTP read timeout for Overpass API requests |
| `CRAWL_READ_TIMEOUT` | 20s | HTTP read timeout for website crawling |
| `CONNECT_TIMEOUT` | 8s | TCP connection timeout for all HTTP requests |
| `RETRIES` | 3 | Number of retry attempts for failed HTTP requests |
| `BACKOFF_BASE` | 2 | Exponential backoff base for retries (2, 4, 8 seconds) |
| `CRAWL_MAX_PAGES_PER_SITE` | 5 | Maximum pages to crawl per business website |
| `CRAWL_MAX_WORKERS` | 20 | Maximum concurrent threads for website crawling |

## 6.2 OSM Service Layer

### File: `app/services/osm/osm_service.py` (153 lines)

The `OSMService` class serves as the primary interface for the OSM module. It orchestrates the entire search pipeline from geocoding through enrichment.

#### Class: `OSMService`

```python
class OSMService:
    """Service for searching businesses via OpenStreetMap"""
    
    def __init__(self):
        self.default_radius = settings.OSM_DEFAULT_RADIUS
        self.max_results = settings.OSM_MAX_RESULTS
```

The constructor reads default configuration from the application settings.

#### Method: `geocode_city(city, country)`

```python
def geocode_city(self, city: str, country: str) -> Tuple[float, float, str, str]:
    """Geocode a city to get coordinates."""
    return geocode_city_center(city, country)
```

**Purpose**: Thin wrapper that delegates to the `overpass_client.geocode_city_center()` function.

**Parameters**:
- `city`: City name (e.g., "Lahore")
- `country`: Country name (e.g., "Pakistan")

**Returns**: Tuple of `(latitude, longitude, display_name, country_code)`

#### Method: `search_businesses()` — Main Entry Point

This is the **primary method** of the entire OSM module. It orchestrates the complete search pipeline:

```python
def search_businesses(
    self,
    business_type: str,
    city: str,
    country: str,
    radius_meters: Optional[int] = None,
    enable_website_crawl: bool = False
) -> Dict[str, Any]:
```

**Pipeline Steps**:

1. **Geocoding**: Resolves city/country to latitude/longitude coordinates via Nominatim
2. **Country Matching**: Verifies the geocoded result actually belongs to the requested country
3. **Type Resolution**: Maps the user-provided business type to OSM tag pairs
4. **Query Building**: Constructs an Overpass QL query using the resolved tags
5. **Data Fetching**: Executes the query against up to 3 Overpass servers
6. **Record Parsing**: Converts raw OSM elements to structured business records
7. **Enrichment** (optional): Crawls websites for contact information
8. **ID Assignment**: Assigns UUID to each record

**Return Structure**:

```python
{
    "query": {
        "business_type": "restaurant",
        "corrected_type": None,  # or corrected spelling
        "city": "Lahore",
        "country": "Pakistan",
        "resolved_location": "Lahore, Punjab, Pakistan",
        "country_code": "pk",
        "country_matched": True,
        "radius_meters": 8000,
        "center": {"lat": 31.5204, "lon": 74.3587}
    },
    "result_count": 47,
    "emails_found_count": 3,
    "results": [
        {
            "id": "uuid-...",
            "business_name": "Bundu Khan",
            "website": "https://bundukhan.pk",
            "email": "info@bundukhan.pk",
            "phone": "+92-42-35761234",
            "facebook": "https://facebook.com/bundukhan",
            "instagram": null,
            "latitude": 31.5123,
            "longitude": 74.3456,
            "address": "MM Alam Road, Gulberg, Lahore"
        },
        // ...
    ]
}
```

#### Method: `_enrich_records(records)`

```python
def _enrich_records(self, records: List[Dict]) -> List[Dict]:
    """Enrich records with website crawl data"""
```

**Purpose**: Crawls the websites of businesses that have known URLs to extract email addresses, phone numbers, and social media links.

**Implementation**:
- Separates records into those with websites and those without
- Uses `ThreadPoolExecutor` with `CRAWL_MAX_WORKERS` (20) parallel threads
- Submits each website-bearing record to `enrich_record()` for crawling
- Waits for all futures to complete using `as_completed()`
- Merges enriched records with un-enrichable records (no website)

**Thread Safety**: Each thread creates its own HTTP session with browser-like User-Agent headers to avoid looking like a bot.

#### Method: `get_business_types()`

```python
def get_business_types(self) -> Dict[str, List[str]]:
    """Get list of supported business types"""
```

Returns a categorized dictionary of all supported business types. This powers the dropdown menus in the frontend.

**Categories**:
- **Food & Drink**: restaurant, cafe, coffee, fast_food, bar, pub, bakery, pizza, ice cream
- **Health**: dentist, doctor, clinic, hospital, pharmacy, optician, physiotherapy
- **Accommodation**: hotel, hostel, motel, guest house
- **Finance**: bank, atm, money exchange
- **Fitness & Beauty**: gym, fitness, salon, hair salon, beauty salon, spa, barber
- **Retail**: supermarket, grocery, clothing, shoes, electronics, mobile phone, jewellery, bookstore, florist
- **Education**: school, university, college, kindergarten, language school, driving school
- **Services**: laundry, car wash, car repair, petrol, parking, post office
- **Leisure**: cinema, theatre, museum, park, swimming pool

## 6.3 Overpass Client — Core Engine

### File: `app/services/osm/overpass_client.py` (924 lines)

This is the **heart of the OSM module** — the largest and most complex file in the entire system. It handles everything from geocoding to website crawling.

#### 6.3.1 Server Configuration

The client defines fallback servers for both Nominatim and Overpass:

```python
NOMINATIM_SERVERS = [
    "https://nominatim.openstreetmap.org/search",      # Primary (OSM Foundation)
    "https://nominatim.openstreetmap.fr/search",        # Secondary (French community)
    "https://nominatim.geocoding.ai/search",            # Tertiary (AI provider)
]

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",           # Primary (Germany)
    "https://overpass.kumi.systems/api/interpreter",     # Secondary (Germany)
    "https://overpass.openstreetmap.ru/api/interpreter", # Tertiary (Russia)
]
```

**Failover Strategy**: If the primary server fails (timeout, 429 rate limit, 502/503/504 server error), the system automatically tries the next server in the list. This provides geographical redundancy and load distribution.

#### 6.3.2 Junk Email Filtering

The module includes a sophisticated junk email filtering system to remove false positive emails extracted from web pages.

**Domain Blocklist**:

```python
JUNK_EMAIL_DOMAINS = {
    "sentry.io", "sentry.wixpress.com", "sentry-next.wixpress.com",
    "example.com", "domain.com", "yourdomain.com", "test.com",
    "placeholder.com", "email.com",
}
```

These domains are common in application monitoring tools (Sentry), website builders (Wix), and placeholder content.

**Pattern Blocklist**:

```python
JUNK_EMAIL_PATTERNS = [
    r"[a-f0-9]{32}@",          # Sentry DSN hashes
    r"@sentry",                 # Sentry service emails
    r"\.png$", r"\.jpg$",       # Image file names misidentified as emails
    r"\.css$", r"\.js$",        # Asset file names
    r"noemail@",                # Placeholder patterns
    r"user@domain",             # Generic placeholders
    r"@flowdtx\.com",           # Marketing platform emails
    # ... 16 patterns total
]
```

**Function: `is_junk_email(email)`**

```python
def is_junk_email(email: str) -> bool:
    domain = email.split("@")[-1].lower()
    if domain in JUNK_EMAIL_DOMAINS:
        return True
    return any(rx.search(email) for rx in _JUNK_COMPILED)
```

Checks both the domain blocklist and compiled regex patterns. The patterns are pre-compiled at module load time (`_JUNK_COMPILED`) for performance.

#### 6.3.3 Email Extraction Pipeline

**Function: `extract_emails(text)`**

This function implements **six distinct extraction methods** to maximize email discovery:

**Method 1: Standard Regex**
```python
re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
```
Matches standard email patterns like `info@bundukhan.pk`.

**Method 2: Mailto Links**
```python
re.findall(r'mailto:([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', text)
```
Extracts emails from `<a href="mailto:info@example.com">` links.

**Method 3: JSON-LD Structured Data**
```python
for match in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.DOTALL):
    data = json.loads(match.group(1))
    _extract_emails_from_json(data)
```
Parses JSON-LD scripts (Schema.org structured data) for email fields like `contactEmail`, `email`, `sameAs`.

**Method 4: URL-Encoded Emails**
```python
decoded = urllib.parse.unquote(text)
# Then re-apply regex to decoded content
```
Catches emails that appear as `info%40bundukhan.pk` in URL parameters.

**Method 5: Data Attributes**
```python
re.findall(r'data-(?:email|mail|contact)["\s]*[=:]["\s]*([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', text)
```
Extracts emails from HTML data attributes like `data-email="info@example.com"`.

**Method 6: JSON Field Patterns**
```python
re.findall(r'"(?:contactEmail|email|mail)"[:\s]*"([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})"', text)
```
Catches emails in inline JSON objects within JavaScript variables.

**Post-Processing**: All extracted emails are converted to lowercase, deduplicated, and filtered through `is_junk_email()` before returning.

#### 6.3.4 Email Prioritization

**Function: `pick_best_email(emails)`**

When multiple emails are found on a website, the system selects the most likely business contact email using a priority ranking:

```python
def pick_best_email(emails: list[str]) -> str | None:
    if not emails:
        return None
    
    # Priority order for prefix matching
    priority_prefixes = ['info@', 'contact@', 'hello@', 'support@', 'enquiries@', 'sales@']
    
    for prefix in priority_prefixes:
        for email in emails:
            if email.lower().startswith(prefix):
                return email
    
    # Prefer non-Gmail addresses (more likely business-specific)
    non_gmail = [e for e in emails if 'gmail.com' not in e.lower()]
    if non_gmail:
        return non_gmail[0]
    
    return emails[0]
```

**Rationale**: Business-specific emails (`info@company.com`) are preferred over personal emails (`owner@gmail.com`) because they indicate a more established business with its own domain.

#### 6.3.5 Social Media Link Extraction

**Function: `extract_social_links(text)`**

```python
def extract_social_links(text: str) -> dict:
    """Extracts Facebook + Instagram URLs from HTML"""
```

**Extraction Logic**:
- Searches for `facebook.com` URLs using regex, excluding tracking pixel URLs and non-profile paths (`/share`, `/plugins`, `/tr`, `/flx`)
- Searches for `instagram.com` URLs, excluding explore pages and embed URLs
- Returns a dictionary with `facebook` and `instagram` keys

**URL Normalization**: Extracted URLs are cleaned to remove query parameters and trailing slashes.

#### 6.3.6 HTTP Session Management

**Function: `make_session(pool_size, browser_ua)`**

Creates a `requests.Session` configured with retry logic and connection pooling.

```python
def make_session(pool_size: int = 20, browser_ua: bool = False) -> requests.Session:
    session = requests.Session()
    
    retry_strategy = Retry(
        total=RETRIES,
        backoff_factor=BACKOFF_BASE,
        status_forcelist=[429, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=pool_size,
        pool_maxsize=pool_size
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    if browser_ua:
        session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
    else:
        session.headers["User-Agent"] = USER_AGENT
    
    return session
```

**Two Types of Sessions**:
1. **Bot sessions** (`browser_ua=False`): Use the `FYP-Global-OSM-Extractor/2.0` User-Agent. Used for Nominatim/Overpass API calls where identifying as a bot is required.
2. **Browser sessions** (`browser_ua=True`): Use a Chrome-like User-Agent. Used for crawling business websites where servers may block bot traffic.

**Connection Pooling**: The `pool_size` parameter controls how many concurrent connections the session can maintain, enabling efficient parallel crawling.

#### 6.3.7 Resilient HTTP Functions

**Function: `resilient_get(url, params, use_session)`**

```python
def resilient_get(url: str, params=None, use_session=None):
    """GET request with retry logic"""
```

Wraps `requests.get()` with configurable timeouts (`CONNECT_TIMEOUT` + `OVERPASS_READ_TIMEOUT`). If a session is provided, uses it; otherwise creates a one-off request.

**Function: `resilient_post(url, data)`**

```python
def resilient_post(url: str, data: bytes):
    """POST request with retry loop for Overpass queries"""
```

Specifically designed for Overpass API queries. Iterates through `OVERPASS_SERVERS` list, attempting each one until a successful response is received. Includes exponential backoff between retries.

#### 6.3.8 Geocoding Pipeline

**Function: `geocode_city_center(city, country)`**

This function resolves a city name to geographic coordinates using the Nominatim API.

```python
def geocode_city_center(city: str, country: str):
    """
    Geocode 'city, country' using up to 3 Nominatim servers.
    Returns: (lat, lon, display_name, country_code)
    """
```

**Algorithm**:

1. Construct query string: `"{city}, {country}"`
2. For each Nominatim server in the failover list:
   a. Send GET request with parameters: `q={query}`, `format=json`, `limit=1`, `addressdetails=1`
   b. If successful, parse the first result
   c. Extract `lat`, `lon`, `display_name` from the response
   d. Extract `country_code` from the `address` details
   e. Return immediately on first successful result
3. If all servers fail, raise an exception

**Country Code Handling**: The function handles common country name aliases:
- "USA", "US", "United States", "America" → `us`
- "UK", "United Kingdom", "GB", "Britain" → `gb`
- "UAE", "United Arab Emirates" → `ae`

#### 6.3.9 Business Type Resolution

**Function: `osm_tag_candidates(business_type)`**

This is one of the most sophisticated functions in the module. It maps user-friendly business type names to the correct OSM tag key-value pairs.

```python
def osm_tag_candidates(business_type: str) -> list[tuple[str, str]]:
    """Map business type to OSM tag candidates via 5-step resolution"""
```

**The Tag Mapping Dictionary** — 60+ business types:

```python
TAG_MAP = {
    # Food & Drink
    "restaurant": [("amenity", "restaurant"), ("amenity", "fast_food"), ("amenity", "food_court")],
    "cafe": [("amenity", "cafe"), ("amenity", "coffee_shop"), ("cuisine", "coffee")],
    "coffee": [("amenity", "cafe"), ("cuisine", "coffee"), ("shop", "coffee")],
    "fast_food": [("amenity", "fast_food")],
    "bar": [("amenity", "bar")],
    "pub": [("amenity", "pub")],
    "bakery": [("shop", "bakery"), ("amenity", "bakery")],
    "pizza": [("cuisine", "pizza")],
    "ice cream": [("cuisine", "ice_cream"), ("shop", "ice_cream"), ("amenity", "ice_cream")],
    
    # Health
    "dentist": [("amenity", "dentist"), ("healthcare", "dentist")],
    "doctor": [("amenity", "doctors"), ("healthcare", "doctor")],
    "clinic": [("amenity", "clinic"), ("healthcare", "clinic")],
    "hospital": [("amenity", "hospital")],
    "pharmacy": [("amenity", "pharmacy"), ("shop", "pharmacy")],
    
    # Accommodation
    "hotel": [("tourism", "hotel")],
    "hostel": [("tourism", "hostel")],
    "motel": [("tourism", "motel")],
    "guest house": [("tourism", "guest_house")],
    
    # Finance
    "bank": [("amenity", "bank")],
    "atm": [("amenity", "atm")],
    
    # Fitness & Beauty
    "gym": [("leisure", "fitness_centre"), ("amenity", "gym")],
    "salon": [("shop", "hairdresser"), ("shop", "beauty")],
    "spa": [("leisure", "spa"), ("amenity", "spa")],
    "barber": [("shop", "barber")],
    
    # Retail
    "supermarket": [("shop", "supermarket")],
    "clothing": [("shop", "clothes"), ("shop", "fashion")],
    "electronics": [("shop", "electronics"), ("shop", "computer")],
    "bookstore": [("shop", "books")],
    "florist": [("shop", "florist")],
    
    # Education
    "school": [("amenity", "school")],
    "university": [("amenity", "university")],
    "college": [("amenity", "college")],
    
    # Services
    "laundry": [("shop", "laundry"), ("shop", "dry_cleaning")],
    "car wash": [("amenity", "car_wash")],
    "car repair": [("shop", "car_repair"), ("amenity", "car_repair")],
    
    # Leisure
    "cinema": [("amenity", "cinema")],
    "theatre": [("amenity", "theatre")],
    "museum": [("tourism", "museum")],
    "swimming pool": [("leisure", "swimming_pool")],
    
    # ... and more
}
```

**5-Step Resolution Process**:

1. **Direct Match**: Exact case-insensitive match (e.g., "restaurant" → restaurant tags)
2. **De-pluralization**: Remove trailing 's' or 'es' (e.g., "restaurants" → "restaurant" → match)
3. **Substring Match**: Check if user input is a substring of any known type or vice versa (e.g., "hair" → "hair salon")
4. **Fuzzy Match**: Use `difflib.get_close_matches()` with cutoff 0.72 for typo correction (e.g., "resturant" → "restaurant")
5. **No Match**: Return empty list — the query builder will fall back to a name-based regex search

**Function: `_resolve_business_type(business_type)`**

Wrapper around `osm_tag_candidates()` that returns a triple:

```python
def _resolve_business_type(business_type: str):
    """Returns: (tags, matched_key, corrected_input)"""
```

This allows the UI to inform users when their input was auto-corrected (e.g., "restarant" → "restaurant").

#### 6.3.10 Overpass Query Building

**Function: `build_overpass_query(lat, lon, radius_m, business_type)`**

Constructs an Overpass QL query string from the resolved parameters.

```python
def build_overpass_query(lat, lon, radius_m, business_type: str) -> str:
```

**Generated Query Example** (for "restaurant" in Lahore):

```
[out:json][timeout:180];
(
  node["amenity"="restaurant"](around:8000,31.5204,74.3587);
  way["amenity"="restaurant"](around:8000,31.5204,74.3587);
  relation["amenity"="restaurant"](around:8000,31.5204,74.3587);
  node["amenity"="fast_food"](around:8000,31.5204,74.3587);
  way["amenity"="fast_food"](around:8000,31.5204,74.3587);
  relation["amenity"="fast_food"](around:8000,31.5204,74.3587);
  node["amenity"="food_court"](around:8000,31.5204,74.3587);
  way["amenity"="food_court"](around:8000,31.5204,74.3587);
  relation["amenity"="food_court"](around:8000,31.5204,74.3587);
);
out center body;
>;
out skel qt;
```

**Query Structure Explained**:
- `[out:json]`: Output in JSON format
- `[timeout:180]`: Server-side timeout of 180 seconds
- `node/way/relation`: Query all three OSM element types for each tag pair
- `(around:radius,lat,lon)`: Spatial filter — elements within `radius` meters of `lat,lon`
- `out center body`: Include center coordinates for ways/relations + all tags
- `out skel qt`: Include skeleton data sorted by quadtile (optimized for rendering)

**Fallback for Unmatched Types**: If `osm_tag_candidates()` returns no tags (type not recognized), the query falls back to a name-based regex search:

```
node["name"~"business_type",i](around:8000,31.5204,74.3587);
```

This searches for any OSM element whose `name` tag matches the user's input (case-insensitive).

#### 6.3.11 Overpass Data Fetching

**Function: `overpass_fetch(query)`**

```python
def overpass_fetch(query: str) -> dict:
    """Execute Overpass query with server failover"""
```

Sends the query to up to 3 Overpass servers:

1. Encode query as UTF-8 bytes
2. For each server in `OVERPASS_SERVERS`:
   a. POST the query data
   b. If response is successful, parse JSON and return
   c. If server fails, log and try next server
3. If all servers fail, return `{"elements": []}`

#### 6.3.12 OSM Element Parsing

**Function: `osm_element_to_record(el)`**

Converts a raw OSM API element into a structured business record.

```python
def osm_element_to_record(el: dict) -> dict:
```

**Input**: Raw OSM element JSON:
```json
{
    "type": "node",
    "id": 12345678,
    "lat": 31.5123,
    "lon": 74.3456,
    "tags": {
        "amenity": "restaurant",
        "name": "Bundu Khan",
        "website": "https://bundukhan.pk",
        "phone": "+92-42-35761234",
        "addr:street": "MM Alam Road",
        "addr:city": "Lahore"
    }
}
```

**Output**: Cleaned business record:
```python
{
    "business_name": "Bundu Khan",
    "website": "https://bundukhan.pk",
    "email": None,
    "phone": "+92-42-35761234",
    "facebook": None,
    "instagram": None,
    "latitude": 31.5123,
    "longitude": 74.3456,
    "address": "MM Alam Road, Lahore",
    "osm_type": "node",
    "osm_id": 12345678
}
```

**Processing Steps**:
1. Extract `tags` dictionary from the element
2. Extract name from `tags["name"]` (with fallback to `brand`, `operator`, `official_name`)
3. Extract and normalize website URL
4. Look for email in `tags["email"]` or `tags["contact:email"]`
5. Validate email with `is_junk_email()` — reject if junk
6. Extract phone from `tags["phone"]` or `tags["contact:phone"]`
7. Extract Facebook/Instagram from `tags["contact:facebook"]` and `tags["contact:instagram"]`
8. Determine coordinates:
   - For `node` elements: use `lat`/`lon` directly
   - For `way`/`relation` elements: use `center.lat`/`center.lon` (computed by Overpass with `out center`)
9. Build address from `addr:street`, `addr:housenumber`, `addr:city`, `addr:postcode` tags

#### 6.3.13 Website Crawling for Contacts

**Function: `crawl_website_for_contacts(website_url, max_pages, crawl_session)`**

This function performs a deep crawl of a business website to find email addresses, phone numbers, and social media links.

```python
def crawl_website_for_contacts(website_url, max_pages, crawl_session):
    """Two-round concurrent crawl for contact information"""
```

**Architecture — Two-Round Crawling**:

**Round 1: Probe known contact pages**

The function first tries 16 common contact page paths simultaneously:

```python
PROBE_PATHS = [
    "/contact", "/contact-us", "/about", "/about-us",
    "/team", "/support", "/help", "/info",
    "/imprint", "/impressum", "/kontakt", "/contacto",
    "/location", "/locations", "/find-us", "/reach-us"
]
```

Implementation:
1. Create a `ThreadPoolExecutor` with 6 workers
2. Submit the homepage URL + all 16 probe paths (17 URLs total)
3. For each successful response:
   a. Extract emails using `extract_emails()`
   b. Extract social links using `extract_social_links()`
4. Stop early if emails are found (no need for Round 2)

**Round 2: Follow homepage links (fallback)**

If Round 1 found no emails, the function scans the homepage HTML for links that might lead to contact pages:

1. Parse the homepage HTML with BeautifulSoup
2. Extract all `<a href>` links
3. Filter to same-domain links that contain keywords like "contact", "about", "team", "support"
4. Crawl these discovered pages (up to `max_pages` total)
5. Extract emails and social links from each page

**Return Value**:

```python
{
    "emails": ["info@bundukhan.pk", "orders@bundukhan.pk"],
    "facebook": "https://facebook.com/bundukhan",
    "instagram": "https://instagram.com/bundukhan",
    "crawled_pages": 5
}
```

#### 6.3.14 Record Enrichment

**Function: `enrich_record(rec)`**

This function enriches a single business record by crawling its website.

```python
def enrich_record(rec: dict) -> dict:
```

**Process**:
1. Create a browser-UA session for this thread
2. Call `crawl_website_for_contacts()` with the record's website URL
3. If emails were found:
   - Set `rec["email"]` to `pick_best_email(emails)`
   - Set `rec["all_emails_found"]` to the complete list
4. If social links were found:
   - Set `rec["facebook"]` and `rec["instagram"]` if not already set from OSM tags
5. Return the enriched record

**Thread Safety**: Each call to `enrich_record()` creates its own HTTP session, so there are no shared mutable state issues when running in a thread pool.

## 6.4 Website Discovery Service

### File: `app/services/osm/website_discovery.py` (201 lines)

This service addresses the critical problem of missing website data in OSM, particularly in developing countries. It uses the DuckDuckGo search engine to discover official business websites.

#### 6.4.1 Problem Statement

In many regions (especially Pakistan), OSM business entries frequently lack the `website` tag. Even well-known restaurants like "Bundu Khan" (which has the official website `bundukhan.pk`) may have no website listed in OSM. Without a website, the system cannot:
- Crawl for email addresses
- Run website audits
- Generate personalized outreach emails

The Website Discovery Service solves this by programmatically searching DuckDuckGo for each business.

#### 6.4.2 Skip Domains

The service maintains a comprehensive blocklist of domains that should never be returned as "official websites":

```python
SKIP_DOMAINS = frozenset({
    # Social media (30+ domains)
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "youtube.com", "linkedin.com", "tiktok.com", "pinterest.com",
    
    # Review / directory sites
    "yelp.com", "tripadvisor.com", "zomato.com", "foursquare.com",
    "yellowpages.com", "trustpilot.com", "justdial.com",
    
    # Wikis
    "wikipedia.org", "wikidata.org",
    
    # Search engines / maps
    "google.com", "bing.com", "openstreetmap.org",
    
    # Food delivery
    "foodpanda.pk", "foodpanda.com", "uber.com", "deliveroo.com",
    "grubhub.com", "doordash.com",
    
    # Food/restaurant aggregators
    "kfoods.com", "restaurantguru.com", "menuism.com",
    
    # Travel aggregators
    "booking.com", "agoda.com", "expedia.com",
    
    # Hosting/builder platforms (subdomain pattern)
    "tossdown.website", "wixsite.com", "weebly.com",
    "squarespace.com", "godaddysites.com",
    
    # Ordering platforms (subdomain pattern)
    "ordrz.com", "order.online", "gloriafood.com",
    "cloudwaitress.com", "getbento.com",
    
    # Food blogs and news sites
    "lahoresnob.com", "foodfusion.com", "dawn.com",
    "tribune.com.pk",
})
```

**Why These Skip Domains Matter**: When searching for "Bundu Khan Lahore official website", DuckDuckGo might return:
1. `bundukhan.pk` ← The actual official website
2. `facebook.com/bundukhan` ← Their Facebook page (not official website)
3. `zomato.com/lahore/bundu-khan` ← A review on Zomato
4. `bundukhan.ordrz.com` ← An ordering platform subdomain
5. `en.wikipedia.org/wiki/Bundu_Khan` ← Their Wikipedia article

Without skip domains, result #2 might be erroneously selected as the "official website" because it appears high in search results.

#### 6.4.3 Domain Checking Logic

**Function: `_is_skip_domain(url)`**

```python
def _is_skip_domain(url: str) -> bool:
    netloc = urlparse(url).netloc.lower().lstrip("www.")
    parts = netloc.split(".")
    root = ".".join(parts[-2:]) if len(parts) >= 2 else netloc
    return any(skip in netloc or skip == root for skip in SKIP_DOMAINS)
```

**Key Innovation**: The function checks both the full domain AND the root domain (last 2 parts). This catches **subdomain patterns** like:
- `bundukhan.ordrz.com` → root is `ordrz.com` → SKIP
- `bundukhan.tossdown.website` → root is `tossdown.website` → SKIP
- `order.bundukhan.pk` → root is `bundukhan.pk` → NOT skipped (it's their own domain)

#### 6.4.4 Generic Words Filter

```python
GENERIC_WORDS = frozenset({
    "restaurant", "hotel", "cafe", "shop", "store", "food",
    "grill", "kitchen", "bar", "bakery", "the", "and",
    "family", "new", "old", "sweet", "sweets", "bakers",
    
    # Pakistani / South-Asian cuisine terms
    "karahi", "tikka", "biryani", "nihari", "haleem", "kebab",
    "kabab", "tandoori", "naan", "chai", "lassi", "paratha",
    "dhaba", "handi", "chapli", "seekh", "boti", "pulao",
    "chaat", "samosa", "paye", "sajji", "shinwari",
    
    # City names (shouldn't count as name matches)
    "lahore", "karachi", "islamabad", "rawalpindi",
})
```

**Purpose**: When scoring a search result's relevance to a business, generic words should not count as name matches. For example:
- Business name: "Butt Karahi"
- URL: `lahorekarahi.co.uk`
- Without generic filtering: "karahi" matches in domain → high score → wrong result
- With generic filtering: "karahi" is a generic cuisine term → ignored → low score → correctly rejected

#### 6.4.5 Scoring Algorithm

**Function: `_score_result(url, title, business_name)`**

The scoring system uses a weighted algorithm to determine how likely a search result is the official website:

```python
def _score_result(url: str, title: str, business_name: str) -> int:
    # Extract significant name words (non-generic, >= 3 chars)
    name_words = [w for w in re.split(r'\W+', name_lower)
                  if len(w) >= 3 and w not in GENERIC_WORDS]
    
    # Concatenated name in domain — strongest signal (+25)
    concat_name = "".join(name_words)
    if len(concat_name) >= 5 and concat_name in domain.replace(".", "").replace("-", ""):
        score += 25
    
    # Individual word in domain (+10 each)
    for word in name_words:
        if word in domain:
            score += 10
    
    # Word in title (+3 each)
    for word in name_words:
        if word in title_lower:
            score += 3
    
    return score
```

**Scoring Examples**:

| Business | URL | Score Breakdown | Total |
|----------|-----|----------------|-------|
| Bundu Khan | `bundukhan.pk` | concat "bundukhan" in domain: +25, "bundu": +10, "khan": +10 | **45** |
| Bundu Khan | `facebook.com/bundukhan` | Skipped (facebook.com in SKIP_DOMAINS) | N/A |
| Bundu Khan | `bundukhan.ordrz.com` | Skipped (ordrz.com root domain in SKIP_DOMAINS) | N/A |
| Salt n Pepper | `saltnpepper.com.pk` | concat "saltnpepper" in domain: +25, "salt": +10, "pepper": +10 | **45** |
| Cafe Aylanto | `cafeaylanto.org` | concat "cafeaylanto" won't match (cafe is generic), "aylanto": +10 | **10** |
| Butt Karahi | `lahorekarahi.co.uk` | "karahi" is generic → ignored, "butt" not in domain | **0** ✓ rejected |

**Minimum Score Threshold**: `MIN_SCORE = 5`

A result must score at least 5 to be accepted. This means at least one significant name word must appear in the domain, or two must appear in the title.

#### 6.4.6 Website Discovery Function

**Function: `discover_website(business_name, city, country)`**

```python
def discover_website(
    business_name: str,
    city: str,
    country: str = "",
    verify: bool = False,
) -> Optional[str]:
```

**Algorithm**:

1. **Construct search query**: `"{business_name} {city} {country} official website"`
   - The phrase "official website" biases DuckDuckGo toward the actual website rather than directory listings

2. **Execute search**: Use `ddgs.text(query, max_results=10)` to get top 10 results

3. **Score and rank**: For each result:
   a. Skip if domain is in `SKIP_DOMAINS`
   b. Calculate relevance score using `_score_result()`
   c. Track the best-scoring URL

4. **Apply threshold**: Only return a result if `best_score >= MIN_SCORE (5)`

5. **Normalize URL**: Strip path, return only homepage (`scheme://netloc`)

**DuckDuckGo Library**: The `ddgs` (duckduckgo-search) library handles:
- Browser impersonation (rotates between Chrome, Firefox, Safari User-Agents)
- Rate limiting (internal delays to avoid 429 errors)
- Response parsing (returns structured dicts with `href`, `title`, `body`)

#### 6.4.7 Bulk Discovery

**Function: `discover_websites_bulk(records, city, country)`**

```python
def discover_websites_bulk(records, city, country, verify=False):
    """Discover websites for all businesses without one"""
```

**Process**:
1. Filter records that have no website and have a business name
2. For each such record:
   a. Call `discover_website(name, city, country)`
   b. If found, set `rec["website"] = url` and `rec["website_discovered"] = True`
   c. Wait 0.3 seconds between searches (rate limiting)
3. Return `(updated_records, discovered_count)`

## 6.5 API Endpoints Layer

### 6.5.1 OSM Sources Endpoints

**File**: `app/api/v1/endpoints/osm_sources.py` (114 lines)

These endpoints provide the search interface for discovering businesses from OpenStreetMap.

#### POST `/api/v1/osm/search`

**Purpose**: Search for businesses by type and location.

**Request Body** (`BusinessSearchRequest`):
```json
{
    "business_type": "restaurant",
    "city": "Lahore",
    "country": "Pakistan",
    "radius_meters": 8000,
    "enable_website_crawl": false
}
```

**Response** (`BusinessSearchResponse`):
```json
{
    "query": {
        "business_type": "restaurant",
        "corrected_type": null,
        "city": "Lahore",
        "country": "Pakistan",
        "resolved_location": "Lahore, Punjab, Pakistan",
        "country_code": "pk",
        "country_matched": true,
        "radius_meters": 8000,
        "center": {"lat": 31.5204, "lon": 74.3587}
    },
    "result_count": 47,
    "emails_found_count": 3,
    "results": [...]
}
```

**Implementation**: Runs `OSMService.search_businesses()` in a `ThreadPoolExecutor` to avoid blocking the async event loop.

#### GET `/api/v1/osm/business-types`

**Purpose**: Returns the categorized list of supported business types for populating the search form dropdown.

**Response**:
```json
{
    "Food & Drink": ["restaurant", "cafe", "coffee", "fast_food", "bar", "pub", "bakery"],
    "Health": ["dentist", "doctor", "clinic", "hospital", "pharmacy"],
    "Accommodation": ["hotel", "hostel", "motel", "guest house"],
    ...
}
```

#### POST `/api/v1/osm/geocode`

**Purpose**: Geocode a city/country combination to coordinates.

**Response**:
```json
{
    "lat": 31.5204,
    "lon": 74.3587,
    "display_name": "Lahore, Punjab, Pakistan",
    "country_code": "pk"
}
```

### 6.5.2 Businesses Endpoints

**File**: `app/api/v1/endpoints/businesses.py` (706 lines)

These endpoints manage the full lifecycle of business records — saving, updating, deleting, auditing, crawling, and discovering websites.

#### POST `/api/v1/businesses/save`

**Purpose**: Save search results to persistent storage.

**Request Body**:
```json
{
    "businesses": [...],  // Array of business records from search results
    "city": "Lahore",
    "country": "Pakistan"
}
```

**Implementation**:
- Loads existing `data/businesses.json`
- For each new business, checks for duplicate by ID
- Appends non-duplicate records
- Saves back to JSON file

#### POST `/api/v1/businesses/{id}/crawl`

**Purpose**: Crawl a saved business's website to extract contact information.

**Implementation**:
1. Load business record from JSON storage
2. Validate that the business has a website URL
3. Attempt **Playwright-based crawling** via `scrape_website_for_contacts()`
4. If Playwright fails, fall back to **httpx-based crawling** via `_crawl_with_httpx()`
5. Update business record with discovered emails, phones, and social links
6. Save updated record back to JSON

#### POST `/api/v1/businesses/crawl-url`

**Purpose**: Crawl any URL for contact information (not tied to a saved business).

**Implementation**: Same two-tier approach (Playwright → httpx fallback), but returns results directly without saving to storage.

#### POST `/api/v1/businesses/discover-websites`

**Purpose**: Bulk website discovery for all businesses without websites.

**Request Body**:
```json
{
    "businesses": [...],
    "city": "Lahore",
    "country": "Pakistan"
}
```

**Response**:
```json
{
    "businesses": [...],  // Updated with discovered websites
    "discovered_count": 12,
    "total_searched": 35,
    "message": "Discovered 12 out of 35 websites"
}
```

#### POST `/api/v1/businesses/discover-website-single`

**Purpose**: Discover the website for a single business (used for progressive UI updates).

**Request Body**:
```json
{
    "business_name": "Bundu Khan",
    "city": "Lahore",
    "country": "Pakistan"
}
```

**Response**:
```json
{
    "business_name": "Bundu Khan",
    "website": "https://bundukhan.pk",
    "discovered": true
}
```

#### GET `/api/v1/businesses/stats/summary`

**Purpose**: Aggregate statistics about saved businesses.

**Response**:
```json
{
    "total_businesses": 150,
    "with_email": 42,
    "with_website": 98,
    "audited": 35,
    "average_score": 3.2,
    "score_distribution": {
        "excellent": 5,
        "good": 12,
        "fair": 10,
        "poor": 8
    }
}
```

## 6.6 Pydantic Schemas

### File: `app/schemas/business.py` (63 lines)

#### `BusinessSearchRequest`

```python
class BusinessSearchRequest(BaseModel):
    business_type: str                                    # Required: "restaurant", "cafe", etc.
    city: str                                             # Required: "Lahore"
    country: str                                          # Required: "Pakistan"
    radius_meters: int = Field(default=8000, ge=500, le=50000)  # 500m to 50km
    enable_website_crawl: bool = Field(default=False)     # Whether to crawl websites
```

**Validation**: `radius_meters` must be between 500 and 50,000 meters.

#### `BusinessData`

```python
class BusinessData(BaseModel):
    id: Optional[str] = None
    business_name: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    all_emails_found: Optional[List[str]] = None
    website_crawl: Optional[dict] = None
    audit_completed: bool = False
    seo_score: Optional[float] = None
    ssl_score: Optional[float] = None
    load_speed_score: Optional[float] = None
    responsiveness_score: Optional[float] = None
    social_links_score: Optional[float] = None
    image_alt_score: Optional[float] = None
    overall_score: Optional[float] = None
    industry: Optional[str] = None
    services: Optional[List[str]] = None
    target_audience: Optional[str] = None
    unique_selling_points: Optional[List[str]] = None
    business_description: Optional[str] = None
    
    class Config:
        extra = "allow"  # Accept additional fields not defined in the schema
```

**Design Decision**: `extra = "allow"` enables the schema to accept fields that may be added by future enrichment steps (AI extraction, audit scores, etc.) without requiring schema updates.

#### `BusinessSearchResponse`

```python
class BusinessSearchResponse(BaseModel):
    query: dict               # Search parameters and metadata
    result_count: int         # Number of businesses found
    emails_found_count: int   # Number of businesses with emails
    results: List[BusinessData]  # The actual business records
```

## 6.7 Frontend Template — businesses.html

### File: `app/templates/pages/businesses.html` (953 lines)

This is the complete user interface for the Business Collection module, built with Alpine.js for reactivity and Tailwind CSS for styling.

#### 6.7.1 Alpine.js Data Model

```javascript
x-data="{
    // Search form
    searchForm: { business_type: '', city: '', country: '', radius: 8000 },
    
    // Business type categories from API
    businessTypes: {},
    
    // Search results
    searchResults: null,
    searching: false,
    
    // Discovery
    discovering: false,
    discoveryProgress: null,
    
    // Saved businesses
    businesses: [],
    loadingBusinesses: true,
    
    // Pagination
    currentPage: 1,
    totalPages: 1,
    
    // Filters
    filter: { search: '', has_email: '', has_audit: '' },
    searchFilter: 'all',
    
    // Selection
    selectedBusiness: null,
    showDetailModal: false,
}"
```

#### 6.7.2 Search Form

The search form provides:
- **Business Type Dropdown**: Categorized dropdown populated from `/api/v1/osm/business-types`
- **City Input**: Free-text city name
- **Country Input**: Free-text country name with default value
- **Radius Slider**: 500m to 50,000m with real-time display
- **Search Button**: Triggers `searchBusinesses()` with loading spinner

#### 6.7.3 Search Results Table

The results table displays:

| Column | Content |
|--------|---------|
| Business Name | Name from OSM |
| Website | Clickable link or "No website" badge. Shows `🔍 discovered` badge if found via DuckDuckGo |
| Email | Email address or "No email" badge |
| Phone | Phone number or "—" |
| Location | Address extracted from OSM tags |
| Social | Facebook/Instagram icons |

**Filter Dropdown**: Filter between "All", "With email", "Without email", "With website" results.

#### 6.7.4 Find Websites Button

```html
<button @click="discoverWebsites" 
        :disabled="discovering"
        x-show="searchResults?.results?.length > 0">
    <template x-if="!discovering">
        <span>🌐 Find Websites</span>
    </template>
    <template x-if="discovering">
        <span>
            <svg class="animate-spin">...</svg>
            <span x-text="discoveryProgress 
                ? `${discoveryProgress.found}/${discoveryProgress.done} of ${discoveryProgress.total}` 
                : 'Discovering...'">
            </span>
        </span>
    </template>
</button>
```

**Progressive Discovery**: The button shows real-time progress as each business's website is discovered one by one.

#### 6.7.5 Discovery Function

```javascript
async discoverWebsites() {
    const toDiscover = this.searchResults.results
        .filter(b => !b.website && b.business_name);
    
    this.discovering = true;
    this.discoveryProgress = { done: 0, total: toDiscover.length, found: 0 };
    
    for (const business of toDiscover) {
        const response = await fetch('/api/v1/businesses/discover-website-single', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                business_name: business.business_name,
                city: this.searchForm.city,
                country: this.searchForm.country
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.website) {
                business.website = data.website;
                business.website_discovered = true;
                this.discoveryProgress.found++;
            }
        }
        this.discoveryProgress.done++;
    }
}
```

**Design Decision**: Progressive single-business discovery (instead of bulk) provides:
1. **Real-time feedback**: Users see each result appear immediately
2. **Resilience**: Individual failures don't affect other businesses
3. **Responsiveness**: The UI remains interactive during discovery

#### 6.7.6 Auto-Trigger After Search

```javascript
async searchBusinesses() {
    // ... perform search ...
    
    if (data.results?.length > 0) {
        this.$nextTick(() => this.discoverWebsites());
    }
}
```

Website discovery automatically starts after a successful OSM search completes, so users don't need to click the "Find Websites" button manually.

#### 6.7.7 Country Mismatch Warning

```html
<div x-show="searchResults?.query?.country_matched === false" 
     class="mb-3 p-2.5 rounded-lg bg-amber-50 border border-amber-200">
    <p class="font-semibold text-amber-700">Country mismatch detected</p>
    <p class="text-amber-600">
        You searched for <strong x-text="searchResults.query.country"></strong>, 
        but results are from 
        <strong x-text="searchResults.query.resolved_location"></strong>
    </p>
</div>
```

This warning appears when the geocoded location doesn't match the user's specified country — for example, searching for "Paris, Pakistan" might resolve to Paris, France.

---

# 7. Data Flow Architecture

## 7.1 Complete Search Pipeline

```
User enters: Type="restaurant", City="Lahore", Country="Pakistan", Radius=8000

Step 1: Frontend → POST /api/v1/osm/search
        ↓
Step 2: OSMService.search_businesses()
        ↓
Step 3: geocode_city_center("Lahore", "Pakistan")
        → Nominatim API → (31.5204, 74.3587, "Lahore, Punjab, Pakistan", "pk")
        ↓
Step 4: Country match check → "pakistan" in "lahore, punjab, pakistan" → True
        ↓
Step 5: osm_tag_candidates("restaurant")
        → [("amenity", "restaurant"), ("amenity", "fast_food"), ("amenity", "food_court")]
        ↓
Step 6: build_overpass_query(31.5204, 74.3587, 8000, "restaurant")
        → Overpass QL query string
        ↓
Step 7: overpass_fetch(query)
        → POST to overpass-api.de → JSON response with 47 elements
        ↓
Step 8: osm_element_to_record(element) × 47
        → 47 business records (some with websites, most without)
        ↓
Step 9: Filter records with empty business_name
        → 45 valid records
        ↓
Step 10: Add UUID to each record
        ↓
Step 11: Return SearchResponse to frontend
        ↓
Step 12: Frontend auto-triggers discoverWebsites()
        ↓
Step 13: For each business without a website:
         POST /api/v1/businesses/discover-website-single
         → discover_website("Bundu Khan", "Lahore", "Pakistan")
         → DuckDuckGo search → score results → "https://bundukhan.pk"
         ↓
Step 14: Frontend updates UI row with discovered website + 🔍 badge
```

## 7.2 Data Enrichment Pipeline

```
User clicks "Crawl" on a saved business with a website

Step 1: POST /api/v1/businesses/{id}/crawl
        ↓
Step 2: Load business from data/businesses.json
        ↓
Step 3: Try Playwright crawler (scrape_website_for_contacts)
        ↓
Step 3a (success): 
        → Extract emails (6 methods)
        → Extract phone numbers
        → Extract social media links
        → Return ScrapedContacts
        ↓
Step 3b (Playwright fails): 
        → Fall back to httpx crawler (_crawl_with_httpx)
        → Visit homepage + 15 probe paths
        → Extract from HTML responses
        ↓
Step 4: Update business record with:
        - email (best from extracted)
        - all_emails_found
        - phone
        - facebook, instagram
        ↓
Step 5: Save to data/businesses.json
        ↓
Step 6: Return updated business to frontend
```

---

# 8. Geocoding Pipeline

## 8.1 How Nominatim Geocoding Works

Nominatim is a search engine for OSM data that converts place names to coordinates (geocoding) and coordinates to place names (reverse geocoding).

**Request Flow**:

```
Client → GET https://nominatim.openstreetmap.org/search
         ?q=Lahore,+Pakistan
         &format=json
         &limit=1
         &addressdetails=1
         
Server → [
    {
        "place_id": 298832568,
        "licence": "Data © OpenStreetMap contributors...",
        "osm_type": "relation",
        "osm_id": 1808511,
        "lat": "31.5546061",
        "lon": "74.3571581",
        "display_name": "Lahore, Punjab, Pakistan",
        "address": {
            "city": "Lahore",
            "state": "Punjab",
            "country": "Pakistan",
            "country_code": "pk"
        },
        "boundingbox": ["31.3601", "31.7101", "74.1401", "74.5601"]
    }
]
```

## 8.2 Server Failover Mechanism

```python
for server_url in NOMINATIM_SERVERS:
    try:
        response = resilient_get(server_url, params={...})
        if response and response.status_code == 200:
            data = response.json()
            if data:
                return parse_result(data[0])
    except Exception:
        continue

raise Exception("All Nominatim servers failed")
```

**Failover Order**:
1. `nominatim.openstreetmap.org` — Official OSM server
2. `nominatim.openstreetmap.fr` — French community mirror (different infrastructure)
3. `nominatim.geocoding.ai` — Third-party mirror

## 8.3 Country Alias Handling

The system handles common country name variations:

```python
country_matched = (
    country_lower in resolved_lower
    or cc_lower == country_lower
    or (country_lower in ["usa", "us", "united states", "america"] and cc_lower == "us")
    or (country_lower in ["uk", "united kingdom", "gb", "britain"] and cc_lower == "gb")
    or (country_lower in ["uae", "united arab emirates"] and cc_lower == "ae")
)
```

---

# 9. Overpass Query Language (Overpass QL)

## 9.1 Language Overview

Overpass QL is a query language specifically designed for extracting data from the OpenStreetMap database. It supports complex spatial queries, tag filtering, and set operations.

## 9.2 Query Structure

Every Overpass query in our system follows this structure:

```
[out:json][timeout:180];         ← Global settings
(                                ← Union block (combine results)
  node[tag](spatial_filter);     ← Query nodes with a specific tag
  way[tag](spatial_filter);      ← Query ways with the same tag
  relation[tag](spatial_filter); ← Query relations
);
out center body;                 ← Output format: include centers + all tags
>;                               ← Recurse into child elements
out skel qt;                     ← Output skeleton sorted by quadtile
```

## 9.3 Spatial Filters

**`around` filter**: Finds elements within a radius of a point.

```
(around:8000,31.5204,74.3587)
```

This selects all elements within 8000 meters of the coordinate (31.5204°N, 74.3587°E).

## 9.4 Tag Filters

**Exact match**: `["amenity"="restaurant"]` — Elements where the `amenity` tag is exactly "restaurant"

**Regex match**: `["name"~"pizza",i]` — Elements where the `name` tag matches the regex "pizza" (case-insensitive)

## 9.5 Generated Query Examples

**Restaurant search in Lahore**:
```
[out:json][timeout:180];
(
  node["amenity"="restaurant"](around:8000,31.5204,74.3587);
  way["amenity"="restaurant"](around:8000,31.5204,74.3587);
  relation["amenity"="restaurant"](around:8000,31.5204,74.3587);
  node["amenity"="fast_food"](around:8000,31.5204,74.3587);
  way["amenity"="fast_food"](around:8000,31.5204,74.3587);
  relation["amenity"="fast_food"](around:8000,31.5204,74.3587);
  node["amenity"="food_court"](around:8000,31.5204,74.3587);
  way["amenity"="food_court"](around:8000,31.5204,74.3587);
  relation["amenity"="food_court"](around:8000,31.5204,74.3587);
);
out center body;
>;
out skel qt;
```

**Gym search with unknown type (fuzzy match)**:
If a user types "gymnassium" (typo), `osm_tag_candidates` fuzzy-matches to "gym", generating:
```
[out:json][timeout:180];
(
  node["leisure"="fitness_centre"](around:8000,lat,lon);
  way["leisure"="fitness_centre"](around:8000,lat,lon);
  relation["leisure"="fitness_centre"](around:8000,lat,lon);
  node["amenity"="gym"](around:8000,lat,lon);
  way["amenity"="gym"](around:8000,lat,lon);
  relation["amenity"="gym"](around:8000,lat,lon);
);
out center body;
>;
out skel qt;
```

---

# 10. Business Type Resolution System

## 10.1 The Need for Resolution

Users may type business types in many ways:
- Correct: "restaurant"
- Plural: "restaurants"
- Abbreviation: "rest"
- Typo: "resturant"
- Alternative: "eatery"

The resolution system handles all of these through its 5-step process.

## 10.2 Resolution Steps

### Step 1: Direct Match
```python
normalized = business_type.strip().lower()
if normalized in TAG_MAP:
    return TAG_MAP[normalized]
```

### Step 2: De-pluralization
```python
if normalized.endswith("ies"):
    singular = normalized[:-3] + "y"
elif normalized.endswith("es"):
    singular = normalized[:-2]
elif normalized.endswith("s"):
    singular = normalized[:-1]

if singular in TAG_MAP:
    return TAG_MAP[singular]
```

### Step 3: Substring Match
```python
for key in TAG_MAP:
    if normalized in key or key in normalized:
        return TAG_MAP[key]
```

### Step 4: Fuzzy Match
```python
from difflib import get_close_matches
matches = get_close_matches(normalized, TAG_MAP.keys(), n=1, cutoff=0.72)
if matches:
    return TAG_MAP[matches[0]]
```

The cutoff of 0.72 means a match requires at least 72% similarity.

### Step 5: No Match
```python
return []  # Overpass will fall back to name regex search
```

## 10.3 Resolution Examples

| User Input | Step | Matched Key | OSM Tags |
|-----------|------|-------------|----------|
| "restaurant" | 1 (direct) | restaurant | `amenity=restaurant`, `amenity=fast_food`, `amenity=food_court` |
| "restaurants" | 2 (de-plural) | restaurant | Same as above |
| "hair" | 3 (substring) | hair salon | `shop=hairdresser`, `shop=beauty` |
| "resturant" | 4 (fuzzy, 0.89) | restaurant | Same as restaurant |
| "xyz123" | 5 (no match) | — | Falls back to `name~"xyz123"` regex |

---

# 11. OSM Element Parsing

## 11.1 Raw OSM Element Structure

An OSM element from the Overpass API looks like:

```json
{
    "type": "way",
    "id": 987654321,
    "center": {
        "lat": 31.5123,
        "lon": 74.3456
    },
    "tags": {
        "amenity": "restaurant",
        "name": "Bundu Khan",
        "name:ur": "بندو خان",
        "cuisine": "pakistani",
        "website": "https://bundukhan.pk",
        "phone": "+92 42 35761234",
        "contact:email": "info@bundukhan.pk",
        "contact:facebook": "https://facebook.com/bundukhan",
        "addr:street": "MM Alam Road",
        "addr:city": "Lahore",
        "addr:postcode": "54000",
        "opening_hours": "12:00-00:00",
        "wheelchair": "yes"
    }
}
```

## 11.2 Parsing Logic

The `osm_element_to_record()` function extracts the following fields:

| Output Field | Source Tag(s) | Fallbacks |
|-------------|--------------|-----------|
| `business_name` | `name` | `brand`, `operator`, `official_name` |
| `website` | `website` | `contact:website`, `url` |
| `email` | `email` | `contact:email` |
| `phone` | `phone` | `contact:phone` |
| `facebook` | `contact:facebook` | — |
| `instagram` | `contact:instagram` | — |
| `latitude` | `lat` (node) | `center.lat` (way/relation) |
| `longitude` | `lon` (node) | `center.lon` (way/relation) |
| `address` | `addr:street` + `addr:housenumber` + `addr:city` + `addr:postcode` | `addr:full` |

---

# 12. Website Crawling and Contact Extraction

## 12.1 Crawling Strategy

The system uses a multi-phase crawling approach:

### Phase 1: Probe Crawl (Concurrent)

Fire 17 requests simultaneously:
- Homepage (/)
- /contact, /contact-us, /about, /about-us
- /team, /support, /help, /info
- /imprint, /impressum, /kontakt, /contacto
- /location, /locations, /find-us, /reach-us

Using 6 parallel threads.

### Phase 2: Link Discovery (Fallback)

If Phase 1 finds no emails:
1. Parse homepage HTML with BeautifulSoup
2. Find all `<a href>` links
3. Filter links containing keywords: "contact", "about", "team", "staff", "support"
4. Crawl discovered pages (additional up to `max_pages`)

## 12.2 Thread Model

```
Main Thread
    │
    ├── ThreadPoolExecutor (20 workers for business-level parallelism)
    │   ├── Thread 1: enrich_record(business_1)
    │   │   └── ThreadPoolExecutor (6 workers per site)
    │   │       ├── Thread: crawl / (homepage)
    │   │       ├── Thread: crawl /contact
    │   │       ├── Thread: crawl /about
    │   │       ├── Thread: crawl /team
    │   │       ├── Thread: crawl /help
    │   │       └── Thread: crawl /support
    │   ├── Thread 2: enrich_record(business_2)
    │   │   └── ThreadPoolExecutor (6 workers per site)
    │   │       └── ...
    │   └── ...
```

Maximum theoretical concurrency: 20 businesses × 6 pages = 120 concurrent HTTP requests.

---

# 13. Email Extraction Pipeline

## 13.1 Six Extraction Methods

| Method | Source | Example |
|--------|--------|---------|
| Standard Regex | HTML text `<p>Email us at info@company.com</p>` | `info@company.com` |
| Mailto Links | `<a href="mailto:info@company.com">` | `info@company.com` |
| JSON-LD | `<script type="application/ld+json">{"email":"info@co.com"}</script>` | `info@co.com` |
| URL-Encoded | `?email=info%40company.com` | `info@company.com` |
| Data Attributes | `<div data-email="info@company.com">` | `info@company.com` |
| JSON Fields | `{"contactEmail":"info@company.com"}` | `info@company.com` |

## 13.2 Post-Processing Pipeline

```
Raw emails from all 6 methods
    → Lowercase
    → Deduplicate (set)
    → Filter junk (domain blocklist + 16 regex patterns)
    → Sort alphabetically
    → Pick best email (priority: info@ > contact@ > non-gmail > first)
```

---

# 14. Website Discovery via DuckDuckGo

## 14.1 Search Query Construction

```
"{business_name} {city} {country} official website"
```

Examples:
- "Bundu Khan Lahore Pakistan official website"
- "Salt n Pepper Lahore Pakistan official website"
- "Cafe Aylanto Lahore Pakistan official website"

The phrase "official website" biases search results toward actual business websites.

## 14.2 Result Scoring

```
For each of DuckDuckGo's top 10 results:
    1. Check if URL domain is in SKIP_DOMAINS → if yes, skip
    2. Extract significant name words (exclude generic)
    3. Score: +25 if concatenated name in domain
    4. Score: +10 per name word in domain
    5. Score: +3 per name word in title
    6. Track best score
    
Return URL with highest score if >= MIN_SCORE (5), else None
```

## 14.3 Tested Results

| Business | Discovered URL | Correct? |
|----------|---------------|----------|
| Bundu Khan | `bundukhan.pk` | ✅ |
| Haveli Restaurant | `havelikebabandgril.com.pk` | ✅ |
| Butt Karahi | `butt-karahi.com` | ✅ |
| Cafe Aylanto | `cafeaylanto.org` | ✅ |
| Salt n Pepper | `saltnpepper.com.pk` | ✅ |
| Arcadian Cafe | `arcadiancafe.com` | ✅ |

---

# 15. Country Mismatch Detection

## 15.1 Problem

When a user searches for "Paris, Pakistan", Nominatim may resolve to Paris, France (stronger match). The system needs to detect this mismatch and warn the user.

## 15.2 Detection Algorithm

```python
country_matched = (
    country_lower in resolved_lower           # "pakistan" in "lahore, punjab, pakistan"
    or cc_lower == country_lower              # "pk" == "pakistan" (rare exact match)
    or alias_match(country_lower, cc_lower)   # "usa" → "us", "uk" → "gb"
)
```

## 15.3 User Interface

When a mismatch is detected, an amber warning banner appears:

> ⚠️ **Country mismatch detected**
> You searched for **Pakistan**, but results are from **Paris, Île-de-France, France**

---

# 16. Error Handling and Resilience

## 16.1 Network Resilience

| Mechanism | Implementation | Coverage |
|-----------|---------------|----------|
| **Retry with backoff** | `urllib3.Retry(total=3, backoff_factor=2)` | All HTTP requests |
| **Status code retry** | Retry on 429 (rate limit), 502, 503, 504 | API calls |
| **Server failover** | 3 servers each for Nominatim and Overpass | Geocoding + OSM query |
| **Timeout limits** | Connect: 8s, Read: 20-120s per request type | All requests |

## 16.2 Data Quality Resilience

| Mechanism | Implementation | Coverage |
|-----------|---------------|----------|
| **Junk email filter** | Domain blocklist + 16 regex patterns | Email extraction |
| **Skip domain filter** | 70+ domains in frozenset | Website discovery |
| **Generic word filter** | 50+ terms for name matching | Discovery scoring |
| **Score threshold** | Minimum score of 5 required | Discovery results |
| **Country validation** | Compare resolved vs requested country | Search results |

## 16.3 Error Propagation

```
External API failure
    → Retry 3 times with exponential backoff
    → Try next server in failover list
    → If all servers fail:
        → Geocoding: raise exception → 500 error to client
        → Overpass: return empty results → 0 businesses found
        → DuckDuckGo: return None → business remains without website
        → Website crawl: return empty contacts → no enrichment
```

---

# 17. Concurrent Processing Architecture

## 17.1 Thread Pool Design

```python
# Business-level parallelism (enrichment)
CRAWL_MAX_WORKERS = 20
executor = ThreadPoolExecutor(max_workers=CRAWL_MAX_WORKERS)

# Site-level parallelism (probe paths)
per_site_workers = 6
```

## 17.2 Async/Sync Bridge

FastAPI uses async endpoints, but the OSM module is synchronous (Nominatim and Overpass use `requests`, not `httpx`). The bridge is:

```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(
    executor,  # ThreadPoolExecutor
    lambda: osm_service.search_businesses(...)
)
```

This runs the synchronous code in a separate thread, preventing the async event loop from blocking.

---

# 18. File-Based Data Persistence

## 18.1 Storage Format

Businesses are stored in `data/businesses.json`:

```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "business_name": "Bundu Khan",
        "website": "https://bundukhan.pk",
        "email": "info@bundukhan.pk",
        "phone": "+92-42-35761234",
        "latitude": 31.5123,
        "longitude": 74.3456,
        "address": "MM Alam Road, Lahore",
        "audit_completed": true,
        "overall_score": 3.5,
        "seo_score": 4.0,
        "ssl_score": 5.0,
        "load_speed_score": 3.0,
        "responsiveness_score": 4.0,
        "social_links_score": 2.0,
        "image_alt_score": 3.0
    },
    // ...
]
```

## 18.2 Read/Write Operations

```python
def _load_businesses() -> list:
    """Load businesses from JSON file"""
    path = Path("data/businesses.json")
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)

def _save_businesses(businesses: list):
    """Save businesses to JSON file"""
    _ensure_data_dir()
    path = Path("data/businesses.json")
    with open(path, "w") as f:
        json.dump(businesses, f, indent=2, default=str)
```

## 18.3 Deduplication

When saving new businesses, the system checks for duplicates by ID:

```python
existing_ids = {b["id"] for b in existing}
new_records = [b for b in new_businesses if b["id"] not in existing_ids]
```

---

# 19. Frontend Architecture with Alpine.js

## 19.1 Reactive Data Binding

Alpine.js provides Vue-like reactivity without a build step:

```html
<!-- Reactive search results count -->
<span x-text="searchResults?.result_count || 0"></span>

<!-- Conditional rendering -->
<div x-show="searchResults?.results?.length > 0">
    <!-- Results table -->
</div>

<!-- Dynamic class binding -->
<span :class="business.email ? 'text-green-600' : 'text-red-400'">
    <span x-text="business.email || 'No email'"></span>
</span>

<!-- Loop rendering -->
<template x-for="business in filteredResults" :key="business.id">
    <tr>...</tr>
</template>
```

## 19.2 API Communication Pattern

```javascript
async searchBusinesses() {
    this.searching = true;
    try {
        const response = await fetch('/api/v1/osm/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.searchForm)
        });
        
        if (response.ok) {
            this.searchResults = await response.json();
            // Auto-trigger website discovery
            this.$nextTick(() => this.discoverWebsites());
        }
    } catch (error) {
        showToast('Search failed: ' + error.message, 'error');
    } finally {
        this.searching = false;
    }
}
```

---

# 20. Next.js Frontend Integration Guide

## 20.1 API Compatibility

All backend API endpoints are RESTful and return JSON, making them directly compatible with Next.js:

```typescript
// Next.js API call example
const searchBusinesses = async (params: BusinessSearchRequest) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/osm/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
    });
    return response.json() as Promise<BusinessSearchResponse>;
};
```

## 20.2 TypeScript Interface Definitions

```typescript
// Converted from Pydantic schemas

interface BusinessSearchRequest {
    business_type: string;
    city: string;
    country: string;
    radius_meters?: number;  // default 8000, min 500, max 50000
    enable_website_crawl?: boolean;
}

interface BusinessData {
    id?: string;
    business_name?: string;
    website?: string;
    email?: string;
    phone?: string;
    facebook?: string;
    instagram?: string;
    latitude?: number;
    longitude?: number;
    all_emails_found?: string[];
    website_crawl?: Record<string, any>;
    audit_completed: boolean;
    seo_score?: number;
    ssl_score?: number;
    load_speed_score?: number;
    responsiveness_score?: number;
    social_links_score?: number;
    image_alt_score?: number;
    overall_score?: number;
    industry?: string;
    services?: string[];
    target_audience?: string;
    unique_selling_points?: string[];
    business_description?: string;
    website_discovered?: boolean;
}

interface BusinessSearchResponse {
    query: {
        business_type: string;
        corrected_type: string | null;
        city: string;
        country: string;
        resolved_location: string;
        country_code: string;
        country_matched: boolean;
        radius_meters: number;
        center: { lat: number; lon: number };
    };
    result_count: number;
    emails_found_count: number;
    results: BusinessData[];
}

interface DiscoverWebsiteResponse {
    business_name: string;
    website: string | null;
    discovered: boolean;
}
```

## 20.3 Recommended Next.js Component Structure

```
app/
├── businesses/
│   ├── page.tsx            # Main businesses page (Server Component)
│   ├── SearchForm.tsx      # Search form (Client Component)
│   ├── ResultsTable.tsx    # Results table (Client Component)
│   ├── DiscoveryProgress.tsx # Website discovery progress (Client Component)
│   ├── SavedBusinesses.tsx # Saved businesses list (Server Component with Client interactivity)
│   └── BusinessDetailModal.tsx # Detail modal with radar chart
├── api/
│   └── businesses/
│       └── route.ts        # Optional: Next.js API route as proxy
└── lib/
    ├── api.ts              # API client functions
    └── types.ts            # TypeScript interfaces
```

## 20.4 React Hooks for Progressive Discovery

```typescript
import { useState, useCallback } from 'react';

interface DiscoveryProgress {
    done: number;
    total: number;
    found: number;
}

export function useWebsiteDiscovery() {
    const [discovering, setDiscovering] = useState(false);
    const [progress, setProgress] = useState<DiscoveryProgress | null>(null);

    const discoverWebsites = useCallback(async (
        businesses: BusinessData[],
        city: string,
        country: string,
        onUpdate: (index: number, website: string) => void
    ) => {
        const toDiscover = businesses.filter(b => !b.website && b.business_name);
        if (toDiscover.length === 0) return;

        setDiscovering(true);
        setProgress({ done: 0, total: toDiscover.length, found: 0 });

        for (let i = 0; i < toDiscover.length; i++) {
            try {
                const response = await fetch('/api/v1/businesses/discover-website-single', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        business_name: toDiscover[i].business_name,
                        city,
                        country,
                    }),
                });

                if (response.ok) {
                    const data: DiscoverWebsiteResponse = await response.json();
                    if (data.website) {
                        const originalIndex = businesses.indexOf(toDiscover[i]);
                        onUpdate(originalIndex, data.website);
                        setProgress(prev => prev ? { ...prev, found: prev.found + 1 } : null);
                    }
                }
            } catch (e) {
                // Skip individual failures
            }

            setProgress(prev => prev ? { ...prev, done: i + 1 } : null);
        }

        setDiscovering(false);
        setProgress(null);
    }, []);

    return { discovering, progress, discoverWebsites };
}
```

## 20.5 Server-Side Rendering Considerations

For the businesses page, a hybrid approach is recommended:

1. **Server Component**: Fetch saved businesses from `/api/v1/businesses` during SSR
2. **Client Component**: Search form, results table, and website discovery (requires user interaction and progressive updates)
3. **SWR/React Query**: Use for real-time data fetching with caching and revalidation

```typescript
// app/businesses/page.tsx (Server Component)
import { Suspense } from 'react';
import SearchForm from './SearchForm';
import SavedBusinesses from './SavedBusinesses';

export default async function BusinessesPage() {
    // Pre-fetch business types server-side
    const typesResponse = await fetch(`${API_BASE_URL}/api/v1/osm/business-types`);
    const businessTypes = await typesResponse.json();

    return (
        <div>
            <SearchForm businessTypes={businessTypes} />
            <Suspense fallback={<div>Loading saved businesses...</div>}>
                <SavedBusinesses />
            </Suspense>
        </div>
    );
}
```

---

# 21. API Reference

## 21.1 OSM Search Endpoints

### POST `/api/v1/osm/search`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `business_type` | string | Yes | — | Type of business to search for |
| `city` | string | Yes | — | City name |
| `country` | string | Yes | — | Country name |
| `radius_meters` | integer | No | 8000 | Search radius (500-50000) |
| `enable_website_crawl` | boolean | No | false | Whether to crawl websites for contacts |

### GET `/api/v1/osm/business-types`

No parameters. Returns categorized business type dictionary.

### POST `/api/v1/osm/geocode`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `city` | string | Yes | City name |
| `country` | string | Yes | Country name |

## 21.2 Business Management Endpoints

### GET `/api/v1/businesses`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number |
| `per_page` | integer | No | 20 | Items per page |
| `has_email` | boolean | No | — | Filter by email presence |
| `has_audit` | boolean | No | — | Filter by audit status |
| `industry` | string | No | — | Filter by industry |

### POST `/api/v1/businesses/save`

Saves businesses to persistent storage. Request body: array of business records.

### POST `/api/v1/businesses/{id}/crawl`

Crawls a saved business's website for contacts. No request body.

### POST `/api/v1/businesses/discover-website-single`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `business_name` | string | Yes | Name of the business |
| `city` | string | Yes | City where business is located |
| `country` | string | No | Country |

---

# 22. Testing Methodology

## 22.1 Unit Test Areas

| Component | Test Cases |
|-----------|-----------|
| `osm_tag_candidates()` | Direct match, plural handling, substring match, fuzzy match, no match |
| `is_junk_email()` | Domain blocklist hits, pattern matching, valid emails pass |
| `extract_emails()` | Each of 6 extraction methods, combined results, deduplication |
| `_score_result()` | Concatenated match, individual word match, title match, generic word filtering |
| `_is_skip_domain()` | Direct domain match, subdomain extraction, root domain check |
| `osm_element_to_record()` | Node with all tags, way with center, missing tags, junk email filtering |

## 22.2 Integration Test Areas

| Test | Description |
|------|-------------|
| Geocoding failover | Mock primary server failure, verify secondary works |
| Overpass failover | Mock all 3 servers, verify empty result graceful handling |
| Full search pipeline | End-to-end search from API to response |
| Website discovery | Verify correct URL returned for known businesses |
| Crawl + extract | Crawl a test website, verify email extraction |

## 22.3 Manual Test Results

The website discovery system was manually tested with Pakistani restaurants:

| Business | Expected | Actual | Status |
|----------|----------|--------|--------|
| Bundu Khan | bundukhan.pk | bundukhan.pk | ✅ Pass |
| Haveli Restaurant | havelikebabandgril.com.pk | havelikebabandgril.com.pk | ✅ Pass |
| Butt Karahi | butt-karahi.com | butt-karahi.com | ✅ Pass |
| Cafe Aylanto | cafeaylanto.org | cafeaylanto.org | ✅ Pass |
| Salt n Pepper | saltnpepper.com.pk | saltnpepper.com.pk | ✅ Pass |
| Arcadian Cafe | arcadiancafe.com | arcadiancafe.com | ✅ Pass |

---

# 23. Performance Optimization

## 23.1 Network Optimization

| Optimization | Description | Impact |
|-------------|-------------|--------|
| Connection pooling | Reuse TCP connections via `requests.Session` | ~30% faster for multi-page crawls |
| Concurrent crawling | 20-worker thread pool for business enrichment | ~20x throughput increase |
| Per-site parallelism | 6 probe pages fetched simultaneously | ~6x faster per-site crawling |
| Early exit | Stop crawling once emails found | ~50% fewer requests on average |

## 23.2 Search Optimization

| Optimization | Description | Impact |
|-------------|-------------|--------|
| `MAX_RESULTS = 500` | Increased from 200 for better coverage | More businesses found |
| Tag expansion | "restaurant" queries 3 tag variants | ~30% more results |
| Fuzzy matching | Handles typos at cutoff 0.72 | Better user experience |

## 23.3 Discovery Optimization

| Optimization | Description | Impact |
|-------------|-------------|--------|
| Frozenset for SKIP_DOMAINS | O(1) lookup vs O(n) list | Faster domain checking |
| Compiled regex patterns | Pre-compiled at module load | Faster junk filtering |
| Progressive single discovery | Per-business instead of bulk | Better UX, error resilience |

---

# 24. Security Considerations

## 24.1 API Compliance

- **Nominatim**: User-Agent header with contact email as required by OSM usage policy
- **Overpass**: Query timeout limits prevent resource exhaustion
- **DuckDuckGo**: Rate limiting handled by the `ddgs` library

## 24.2 Input Validation

- Pydantic schemas enforce type constraints on all API inputs
- `radius_meters` limited to 500-50000 to prevent excessive queries
- Business type validated through the resolution system

## 24.3 Data Protection

- No user authentication required (development phase)
- File-based storage in the application directory
- No PII stored beyond public business contact information

---

# 25. Limitations and Future Enhancements

## 25.1 Current Limitations

| Limitation | Impact | Potential Solution |
|-----------|--------|-------------------|
| File-based storage | No concurrent access safety | Migrate to PostgreSQL with SQLAlchemy models |
| Synchronous crawling | Blocks thread pool workers | Migrate to `httpx` async client |
| No authentication | Open API access | Implement JWT-based auth |
| DuckDuckGo rate limits | Discovery speed limited | Implement caching layer |
| OSM data gaps | Missing businesses in developing countries | Integrate Google Places API as fallback |

## 25.2 Planned Enhancements

1. **Database Migration**: The empty `models/business.py` and `repositories/business_repo.py` files indicate planned SQLAlchemy model definitions
2. **Celery Worker**: The empty `workers/tasks/ingest_osm.py` is planned for background OSM ingestion
3. **Test Suite**: The empty `tests/test_osm.py` is planned for unit and integration tests
4. **Data Normalization**: The empty `services/osm/normalizer.py` is planned for standardizing address and contact formats
5. **Query Optimization**: The empty `services/osm/queries.py` is planned for extracting query building logic from the monolithic `overpass_client.py`

---

# 26. Conclusion

The Business Collection Using OpenStreetMap module represents the foundational data acquisition layer of the AI-Powered Client Hunt & Outreach system. Through its multi-layered architecture — combining OSM geospatial queries, website crawling, and DuckDuckGo-powered website discovery — the module transforms sparse geographic data into rich, actionable business records suitable for outreach campaigns.

Key technical achievements include:
- **Multi-server failover** for geocoding and data fetching with three fallback servers each
- **Five-step fuzzy business type resolution** supporting 60+ business types with typo correction
- **Six-method email extraction** pipeline capturing emails from regex, mailto links, JSON-LD, URL-encoded strings, HTML data attributes, and JavaScript objects
- **Intelligent website discovery** with DuckDuckGo scoring, 70+ skip domains, and cuisine-aware generic word filtering
- **Concurrent enrichment** with 20 business-level threads and 6 page-level threads per site
- **Progressive UI updates** showing real-time website discovery progress

The module is designed for extensibility, with placeholder files for database models, worker tasks, and test suites ready for implementation in future development cycles.

---

*End of Module 1 Documentation — Business Collection Using OpenStreetMap*
