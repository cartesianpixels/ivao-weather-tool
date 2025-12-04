"""
API client for FAA/NOAA Aviation Weather Center.
Handles HTTP requests with retry logic and error handling.
"""

import httpx
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from .models import MetarData, TafData

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    """Base exception for weather API errors."""
    pass


class WeatherAPIClient:
    """Async HTTP client for Aviation Weather Center API."""
    
    BASE_URL = "https://aviationweather.gov/api/data"
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize API client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with exponential backoff retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for httpx request
            
        Returns:
            httpx.Response object
            
        Raises:
            WeatherAPIError: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
                
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
                last_exception = e
                
                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    raise WeatherAPIError(f"Client error: {e}") from e
                    
            except httpx.RequestError as e:
                logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                last_exception = e
            
            # Exponential backoff
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)
        
        # All retries failed
        raise WeatherAPIError(
            f"Failed after {self.max_retries} attempts: {last_exception}"
        ) from last_exception
    
    async def get_metar(
        self,
        stations: List[str],
        hours_before: int = 2
    ) -> List[str]:
        """
        Fetch METAR data for specified stations.
        
        Args:
            stations: List of ICAO station codes
            hours_before: How many hours back to retrieve
            
        Returns:
            List of raw METAR strings
        """
        if not stations:
            return []
        
        # Build query parameters
        params = {
            "ids": ",".join(s.upper() for s in stations),
            "format": "raw",
            "hours": hours_before,
            "taf": "false"
        }
        
        url = f"{self.BASE_URL}/metar"
        
        try:
            response = await self._request_with_retry("GET", url, params=params)
            
            # Parse response - AWC returns plain text, one METAR per line
            text = response.text.strip()
            if not text:
                return []
            
            metars = [line.strip() for line in text.split('\n') if line.strip()]
            logger.info(f"Retrieved {len(metars)} METARs for {len(stations)} stations")
            return metars
            
        except WeatherAPIError as e:
            logger.error(f"Failed to fetch METARs: {e}")
            raise
    
    async def get_taf(
        self,
        stations: List[str],
        hours_before: int = 6
    ) -> List[str]:
        """
        Fetch TAF data for specified stations.
        
        Args:
            stations: List of ICAO station codes
            hours_before: How many hours back to retrieve
            
        Returns:
            List of raw TAF strings
        """
        if not stations:
            return []
        
        params = {
            "ids": ",".join(s.upper() for s in stations),
            "format": "raw",
            "hours": hours_before
        }
        
        url = f"{self.BASE_URL}/taf"
        
        try:
            response = await self._request_with_retry("GET", url, params=params)
            
            text = response.text.strip()
            if not text:
                return []
            
            # TAFs can be multi-line, split by TAF keyword
            tafs = []
            current_taf = []
            
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('TAF'):
                    if current_taf:
                        tafs.append('\n'.join(current_taf))
                    current_taf = [line]
                elif line and current_taf:
                    current_taf.append(line)
            
            if current_taf:
                tafs.append('\n'.join(current_taf))
            
            logger.info(f"Retrieved {len(tafs)} TAFs for {len(stations)} stations")
            return tafs
            
        except WeatherAPIError as e:
            logger.error(f"Failed to fetch TAFs: {e}")
            raise
    
    async def get_pireps(
        self,
        location: Optional[str] = None,
        distance: int = 100,
        hours_before: int = 6
    ) -> List[str]:
        """
        Fetch PIREP data.
        
        Args:
            location: Center point (ICAO code or lat,lon)
            distance: Radius in statute miles
            hours_before: How many hours back to retrieve
            
        Returns:
            List of raw PIREP strings
        """
        params = {
            "format": "raw",
            "hours": hours_before
        }
        
        if location:
            params["id"] = location.upper()
            params["distance"] = distance
        
        url = f"{self.BASE_URL}/pirep"
        
        try:
            response = await self._request_with_retry("GET", url, params=params)
            
            text = response.text.strip()
            if not text:
                return []
            
            pireps = [line.strip() for line in text.split('\n') if line.strip()]
            logger.info(f"Retrieved {len(pireps)} PIREPs")
            return pireps
            
        except WeatherAPIError as e:
            logger.error(f"Failed to fetch PIREPs: {e}")
            raise
    
    async def get_station_info(self, icao: str) -> Optional[Dict[str, Any]]:
        """
        Fetch station information.
        
        Args:
            icao: ICAO station code
            
        Returns:
            Dictionary with station info or None if not found
        """
        # Note: AWC doesn't have a dedicated station info endpoint
        # This is a placeholder for future implementation
        # Could use other sources like OurAirports API
        logger.warning("Station info endpoint not yet implemented")
        return None
    
    async def check_connection(self) -> bool:
        """
        Check if API is reachable.
        
        Returns:
            True if API responds, False otherwise
        """
        try:
            response = await self.client.get(
                "https://aviationweather.gov",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False
