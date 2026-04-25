"""
OSM Business Search Endpoints
"""
import asyncio
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.schemas.business import (
    BusinessSearchRequest,
    BusinessSearchResponse,
    BusinessData
)
from app.services.osm.osm_service import OSMService

router = APIRouter()

# Thread pool for running sync OSM operations
executor = ThreadPoolExecutor(max_workers=4)


@router.post("/search", response_model=BusinessSearchResponse)
async def search_businesses(request: BusinessSearchRequest):
    """
    Search for businesses in a specific location using OpenStreetMap data.
    
    - **business_type**: Type of business (e.g., restaurant, dentist, cafe)
    - **city**: City name
    - **country**: Country name or code
    - **radius_meters**: Search radius in meters (default: 8000)
    - **enable_website_crawl**: Enable crawling websites for contact info
    """
    try:
        osm_service = OSMService()
        
        # Run the synchronous OSM search in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            osm_service.search_businesses,
            request.business_type,
            request.city,
            request.country,
            request.radius_meters,
            request.enable_website_crawl
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business-types")
async def get_business_types():
    """Get list of supported business types for OSM search"""
    return {
        "categories": {
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
    }


@router.post("/geocode")
async def geocode_location(city: str, country: str):
    """
    Geocode a city/country to get coordinates.
    Useful for map display.
    """
    try:
        osm_service = OSMService()
        
        loop = asyncio.get_event_loop()
        lat, lon, display_name, cc = await loop.run_in_executor(
            executor,
            osm_service.geocode_city,
            city,
            country
        )
        
        return {
            "latitude": lat,
            "longitude": lon,
            "display_name": display_name,
            "country_code": cc
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
