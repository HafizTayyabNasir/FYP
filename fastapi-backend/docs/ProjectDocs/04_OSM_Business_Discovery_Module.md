# 04 — OSM Business Discovery Module (Theory + Design)

## 4.1 Purpose

The OSM discovery module is responsible for building a **lead list** from publicly available geospatial data.

The project uses:

- **Nominatim** (geocoding) to convert *city + country* into coordinates.
- **Overpass API** to query OpenStreetMap for businesses around those coordinates.

The output is a list of candidate businesses with attributes such as:

- business name
- category/type
- coordinates
- address
- website
- phone
- social links (optional enrichment)

## 4.2 Why OpenStreetMap (OSM)

OSM is community-maintained and open.

Advantages:

- no paid API required (unlike some commercial map APIs),
- wide coverage for many countries,
- tag-based semantics (amenity, shop, tourism, etc.).

Limitations:

- data completeness varies by city,
- tags can be inconsistent,
- some records lack websites and contact details.

For an FYP, OSM is attractive because it supports research on open data usage.

## 4.3 Geocoding Theory

### 4.3.1 What is geocoding
Geocoding converts a human-readable location into geographic coordinates.

Given input:

- city: `"Lahore"`
- country: `"Pakistan"`

Geocoder returns:

- latitude
- longitude
- a display name (often including region)
- country code

### 4.3.2 Challenges

- **Ambiguity**: many cities share names.
- **Localization**: the same place can have different names.
- **Country mismatch**: a city name could resolve to a different country.

### 4.3.3 Country verification
A robust system performs country verification by:

- checking if requested country appears in geocoder’s display_name,
- matching ISO country code,
- handling common aliases (e.g., US/USA/United States).

This improves precision and reduces false leads.

## 4.4 Overpass Query Theory

### 4.4.1 Overpass
Overpass is a read-only API that allows queries over OSM data.

It supports:

- bounding box queries
- radius queries around a point
- tag queries (amenity=restaurant, shop=clothes, etc.)

### 4.4.2 OSM elements
Overpass returns elements of types:

- **node**: a point
- **way**: a polyline/polygon
- **relation**: a complex structure

Each element includes:

- id
- tags (key/value map)
- coordinates or geometry

### 4.4.3 Business type resolution
Users provide fuzzy business types (e.g., "coffee shop"), but Overpass needs tags.

A resolution layer maps:

- user phrase → candidate tags

Approaches:

1. **Dictionary mapping**: fixed mapping from terms to tags.
2. **Synonym lists**: match common synonyms.
3. **Fuzzy string matching**: Levenshtein distance / token similarity.
4. **LLM-assisted mapping**: translate a phrase into OSM tags (risk: unpredictability).

For a stable system, dictionary + light fuzzy matching is preferred.

## 4.5 Reliability Engineering for OSM

Public OSM APIs impose policies:

- You must provide a correct User-Agent with contact email.
- Excess traffic can lead to blocks.

Reliability patterns:

### 4.5.1 Rotating endpoints
Multiple Nominatim/Overpass endpoints can be used as fallback.

### 4.5.2 Retries and backoff
On transient errors (HTTP 429/502/503/504):

- retry with exponential backoff.

### 4.5.3 Timeouts
Separate timeout profiles are used:

- Overpass: large read timeout (queries can be slow)
- Crawling: smaller timeout (avoid waiting too long on websites)

### 4.5.4 Caching
Recommended caching levels:

- cache geocode results per city+country
- cache overpass query results per type+center+radius

Caching avoids repeated API calls and improves speed.

## 4.6 Data Normalization Theory

### 4.6.1 Why normalize
OSM tags are heterogeneous.

Normalization converts them into a uniform business record schema.

### 4.6.2 Typical fields

- `business_name`
- `category`
- `latitude`, `longitude`
- `address`
- `phone`
- `website`
- `opening_hours`

### 4.6.3 Address building
Address may be composed from multiple tags:

- `addr:housenumber`
- `addr:street`
- `addr:city`
- `addr:postcode`

If missing, fallback to display_name.

## 4.7 Lead Quality Considerations

Not all OSM businesses are good outreach leads.

Quality heuristics:

- has website (required for audit-driven outreach)
- has valid email/contact channel
- category matches user request
- distance from center not too large

In future work, add scoring for lead quality.

## 4.8 Website Enrichment (Optional)

Discovery returns many records with websites but without emails.

Enrichment step can:

- crawl website pages likely to contain contact info
- extract emails, phones, social handles
- choose the best email (info@, contact@, etc.)

This moves the system from “directory data” to “actionable leads”.

## 4.9 Ethics and Terms of Use

OSM services should be used respectfully:

- obey rate limits,
- include a real contact email in User-Agent,
- avoid repeated heavy queries.

Academic reporting should mention:

- the open data nature of OSM,
- limitations in data accuracy,
- respect for community infrastructure.

## 4.10 Evaluation Metrics

For evaluating this module, you can measure:

- **precision**: fraction of returned businesses that match the intended category/location
- **coverage**: number of businesses found
- **website availability rate**: fraction with websites
- **enrichment success**: fraction where emails are found
- **runtime**: average response time for query sizes

## 4.11 Failure Modes

- geocoding returns wrong city
- Overpass servers rate limit
- no results due to tag mismatch
- OSM record missing website

Mitigation:

- interactive refinement of business type
- reduce radius or broaden tags
- fallback endpoints

## 4.12 Summary

The OSM business discovery module provides an open-data-driven foundation for lead generation. By combining geocoding, Overpass querying, and robust normalization/enrichment, the system produces a scalable lead list suitable for website audit and outreach.
