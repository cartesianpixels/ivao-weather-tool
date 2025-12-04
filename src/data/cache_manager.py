"""
Cache manager for IVAO Weather Tool.
Handles caching logic, TTL, and offline mode support.
"""

from typing import Optional, List
from datetime import datetime, timedelta
import logging

from .database import Database
from .api_client import WeatherAPIClient, WeatherAPIError
from .models import MetarData, TafData, UserSettings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages weather data caching and retrieval."""
    
    def __init__(
        self,
        database: Database,
        api_client: WeatherAPIClient,
        cache_ttl_minutes: int = 10
    ):
        """
        Initialize cache manager.
        
        Args:
            database: Database instance
            api_client: API client instance
            cache_ttl_minutes: Cache time-to-live in minutes
        """
        self.db = database
        self.api = api_client
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._online = True
    
    def _is_cache_fresh(self, cached_at: Optional[datetime]) -> bool:
        """Check if cached data is still fresh."""
        if not cached_at:
            return False
        age = datetime.utcnow() - cached_at
        return age < self.cache_ttl
    
    async def get_metar(
        self,
        station: str,
        force_refresh: bool = False
    ) -> Optional[MetarData]:
        """
        Get METAR data, from cache or API.
        
        Args:
            station: ICAO station code
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            MetarData or None if not available
        """
        station = station.upper()
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached = await self.db.get_metar(station)
            if cached and self._is_cache_fresh(cached.cached_at):
                logger.info(f"Using cached METAR for {station}")
                return cached
        
        # Try to fetch fresh data
        try:
            raw_metars = await self.api.get_metar([station])
            
            if raw_metars:
                # TODO: Decode METAR in Phase 3
                # For now, create minimal MetarData
                metar = MetarData(
                    station=station,
                    observation_time=datetime.utcnow(),  # Placeholder
                    raw_text=raw_metars[0],
                    cached_at=datetime.utcnow()
                )
                
                # Save to cache
                await self.db.save_metar(metar)
                logger.info(f"Fetched and cached fresh METAR for {station}")
                self._online = True
                return metar
            else:
                logger.warning(f"No METAR data available for {station}")
                
        except WeatherAPIError as e:
            logger.error(f"API error fetching METAR: {e}")
            self._online = False
            
            # Fall back to stale cache in offline mode
            cached = await self.db.get_metar(station)
            if cached:
                logger.info(f"Using stale cached METAR for {station} (offline mode)")
                return cached
        
        return None
    
    async def get_taf(
        self,
        station: str,
        force_refresh: bool = False
    ) -> Optional[TafData]:
        """
        Get TAF data, from cache or API.
        
        Args:
            station: ICAO station code
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            TafData or None if not available
        """
        station = station.upper()
        
        # Check cache first
        if not force_refresh:
            cached = await self.db.get_taf(station)
            if cached and self._is_cache_fresh(cached.cached_at):
                logger.info(f"Using cached TAF for {station}")
                return cached
        
        # Try to fetch fresh data
        try:
            raw_tafs = await self.api.get_taf([station])
            
            if raw_tafs:
                # TODO: Decode TAF in Phase 3
                # For now, create minimal TafData
                taf = TafData(
                    station=station,
                    issue_time=datetime.utcnow(),  # Placeholder
                    valid_from=datetime.utcnow(),
                    valid_to=datetime.utcnow() + timedelta(hours=24),
                    raw_text=raw_tafs[0],
                    cached_at=datetime.utcnow()
                )
                
                # Save to cache
                await self.db.save_taf(taf)
                logger.info(f"Fetched and cached fresh TAF for {station}")
                self._online = True
                return taf
            else:
                logger.warning(f"No TAF data available for {station}")
                
        except WeatherAPIError as e:
            logger.error(f"API error fetching TAF: {e}")
            self._online = False
            
            # Fall back to stale cache
            cached = await self.db.get_taf(station)
            if cached:
                logger.info(f"Using stale cached TAF for {station} (offline mode)")
                return cached
        
        return None
    
    async def get_multiple_metars(
        self,
        stations: List[str],
        force_refresh: bool = False
    ) -> List[MetarData]:
        """
        Get METARs for multiple stations.
        
        Args:
            stations: List of ICAO station codes
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            List of MetarData objects
        """
        results = []
        
        for station in stations:
            metar = await self.get_metar(station, force_refresh)
            if metar:
                results.append(metar)
        
        return results
    
    async def is_online(self) -> bool:
        """
        Check if we have internet connectivity.
        
        Returns:
            True if online, False if offline
        """
        try:
            is_connected = await self.api.check_connection()
            self._online = is_connected
            return is_connected
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            self._online = False
            return False
    
    async def clear_old_cache(self, max_age_hours: int = 24):
        """
        Clear cache entries older than specified hours.
        
        Args:
            max_age_hours: Maximum age in hours
        """
        await self.db.clear_old_cache(max_age_hours)
        logger.info(f"Cleared cache entries older than {max_age_hours} hours")
    
    def get_cache_status(self) -> dict:
        """
        Get current cache status.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "online": self._online,
            "cache_ttl_minutes": self.cache_ttl.total_seconds() / 60
        }
