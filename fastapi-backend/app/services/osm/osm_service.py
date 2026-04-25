"""
OSM Service - Wrapper for OpenStreetMap business search functionality
"""
import uuid
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.core.config import settings
from app.services.osm.overpass_client import (
    geocode_city_center,
    build_overpass_query,
    overpass_fetch,
    osm_element_to_record,
    enrich_record,
    _resolve_business_type,
    make_session,
    CRAWL_MAX_WORKERS,
    CRAWL_MAX_PAGES_PER_SITE
)


class OSMService:
    """Service for searching businesses via OpenStreetMap"""
    
    def __init__(self):
        self.default_radius = settings.OSM_DEFAULT_RADIUS
        self.max_results = settings.OSM_MAX_RESULTS
    
    def geocode_city(self, city: str, country: str) -> Tuple[float, float, str, str]:
        """
        Geocode a city to get coordinates.
        
        Returns: (latitude, longitude, display_name, country_code)
        """
        return geocode_city_center(city, country)
    
    def search_businesses(
        self,
        business_type: str,
        city: str,
        country: str,
        radius_meters: Optional[int] = None,
        enable_website_crawl: bool = False
    ) -> Dict[str, Any]:
        """
        Search for businesses in a specific location.
        
        Args:
            business_type: Type of business to search for
            city: City name
            country: Country name or code
            radius_meters: Search radius in meters
            enable_website_crawl: Whether to crawl websites for contact info
            
        Returns:
            Dictionary with query info and results
        """
        radius_m = radius_meters or self.default_radius
        
        # Geocode the city
        lat, lon, display_name, cc = geocode_city_center(city, country)
        
        # Check if the resolved country actually matches the requested country
        country_lower = country.strip().lower()
        resolved_lower = (display_name or "").lower()
        cc_lower = cc.lower() if cc else ""
        country_matched = (
            country_lower in resolved_lower
            or cc_lower == country_lower
            or (country_lower in ["usa", "us", "united states", "america"] and cc_lower == "us")
            or (country_lower in ["uk", "united kingdom", "gb", "britain"] and cc_lower == "gb")
            or (country_lower in ["uae", "united arab emirates"] and cc_lower == "ae")
        )
        
        # Resolve business type to OSM tags
        tags, matched_key, corrected = _resolve_business_type(business_type)
        
        # Build and execute Overpass query
        query = build_overpass_query(lat, lon, radius_m, business_type)
        data = overpass_fetch(query)
        
        # Parse results
        elements = data.get("elements", []) or []
        records = [osm_element_to_record(el) for el in elements]
        records = [r for r in records if r.get("business_name")]
        
        # Enrich with website crawl if enabled
        if enable_website_crawl:
            records = self._enrich_records(records)
        
        # Add unique IDs to each record
        for record in records:
            record["id"] = str(uuid.uuid4())
        
        return {
            "query": {
                "business_type": business_type,
                "corrected_type": corrected if corrected != business_type else None,
                "city": city,
                "country": country,
                "resolved_location": display_name,
                "country_code": cc,
                "country_matched": country_matched,
                "radius_meters": radius_m,
                "center": {"lat": lat, "lon": lon}
            },
            "result_count": len(records),
            "emails_found_count": sum(1 for r in records if r.get("email")),
            "results": records
        }
    
    def _enrich_records(self, records: List[Dict]) -> List[Dict]:
        """Enrich records with website crawl data"""
        with_sites = [r for r in records if r.get("website")]
        without = [r for r in records if not r.get("website")]
        
        enriched = []
        with ThreadPoolExecutor(max_workers=CRAWL_MAX_WORKERS) as pool:
            futures = {pool.submit(enrich_record, rec): rec for rec in with_sites}
            for fut in as_completed(futures):
                try:
                    result = fut.result()
                    enriched.append(result)
                except Exception:
                    enriched.append(futures[fut])
        
        return enriched + without
    
    def get_business_types(self) -> Dict[str, List[str]]:
        """Get list of supported business types"""
        return {
            "Food & Drink": [
                "restaurant", "cafe", "coffee", "fast_food", "bar", "pub",
                "bakery", "pizza", "ice cream"
            ],
            "Health": [
                "dentist", "doctor", "clinic", "hospital", "pharmacy",
                "optician", "physiotherapy"
            ],
            "Accommodation": [
                "hotel", "hostel", "motel", "guest house"
            ],
            "Finance": [
                "bank", "atm", "money exchange"
            ],
            "Fitness & Beauty": [
                "gym", "fitness", "salon", "hair salon", "beauty salon",
                "spa", "barber"
            ],
            "Retail": [
                "supermarket", "grocery", "clothing", "shoes", "electronics",
                "mobile phone", "jewellery", "bookstore", "florist"
            ],
            "Education": [
                "school", "university", "college", "kindergarten",
                "language school", "driving school"
            ],
            "Services": [
                "laundry", "car wash", "car repair", "petrol", "parking",
                "post office"
            ],
            "Leisure": [
                "cinema", "theatre", "museum", "park", "swimming pool"
            ]
        }
