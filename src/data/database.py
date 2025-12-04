"""
Database management for IVAO Weather Tool.
SQLite database for caching weather data and storing user preferences.
"""

import aiosqlite
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import json

from .models import MetarData, TafData, PirepData, StationInfo, UserSettings


class Database:
    """Async SQLite database manager."""
    
    def __init__(self, db_path: str = "data/weather_cache.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Establish database connection."""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self._create_tables()
    
    async def close(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
    
    async def _create_tables(self):
        """Create database tables if they don't exist."""
        async with self.connection.cursor() as cursor:
            # METAR cache table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS metar_cache (
                    station TEXT PRIMARY KEY,
                    observation_time TEXT NOT NULL,
                    raw_text TEXT NOT NULL,
                    decoded_data TEXT NOT NULL,
                    flight_category TEXT,
                    cached_at TEXT NOT NULL
                )
            """)
            
            # TAF cache table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS taf_cache (
                    station TEXT PRIMARY KEY,
                    issue_time TEXT NOT NULL,
                    valid_from TEXT NOT NULL,
                    valid_to TEXT NOT NULL,
                    raw_text TEXT NOT NULL,
                    decoded_data TEXT NOT NULL,
                    cached_at TEXT NOT NULL
                )
            """)
            
            # PIREP cache table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS pirep_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT NOT NULL,
                    observation_time TEXT NOT NULL,
                    raw_text TEXT NOT NULL,
                    decoded_data TEXT NOT NULL,
                    cached_at TEXT NOT NULL
                )
            """)
            
            # Station info table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS stations (
                    icao TEXT PRIMARY KEY,
                    name TEXT,
                    latitude REAL,
                    longitude REAL,
                    elevation INTEGER,
                    is_favorite INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)
            
            # User settings table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            # Training progress table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_progress (
                    lesson_id TEXT PRIMARY KEY,
                    completed INTEGER DEFAULT 0,
                    score INTEGER,
                    completed_at TEXT
                )
            """)
            
            await self.connection.commit()
    
    # METAR operations
    async def save_metar(self, metar: MetarData):
        """Save METAR to cache."""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO metar_cache 
                (station, observation_time, raw_text, decoded_data, flight_category, cached_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metar.station,
                metar.observation_time.isoformat(),
                metar.raw_text,
                metar.model_dump_json(),
                metar.flight_category,
                datetime.utcnow().isoformat()
            ))
            await self.connection.commit()
    
    async def get_metar(self, station: str) -> Optional[MetarData]:
        """Retrieve METAR from cache."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT decoded_data FROM metar_cache WHERE station = ?",
                (station.upper(),)
            )
            row = await cursor.fetchone()
            if row:
                return MetarData.model_validate_json(row['decoded_data'])
            return None
    
    # TAF operations
    async def save_taf(self, taf: TafData):
        """Save TAF to cache."""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO taf_cache 
                (station, issue_time, valid_from, valid_to, raw_text, decoded_data, cached_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                taf.station,
                taf.issue_time.isoformat(),
                taf.valid_from.isoformat(),
                taf.valid_to.isoformat(),
                taf.raw_text,
                taf.model_dump_json(),
                datetime.utcnow().isoformat()
            ))
            await self.connection.commit()
    
    async def get_taf(self, station: str) -> Optional[TafData]:
        """Retrieve TAF from cache."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT decoded_data FROM taf_cache WHERE station = ?",
                (station.upper(),)
            )
            row = await cursor.fetchone()
            if row:
                return TafData.model_validate_json(row['decoded_data'])
            return None
    
    # Station operations
    async def save_station(self, station: StationInfo):
        """Save or update station information."""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO stations 
                (icao, name, latitude, longitude, elevation, is_favorite, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                station.icao,
                station.name,
                station.latitude,
                station.longitude,
                station.elevation,
                1 if station.is_favorite else 0,
                station.last_accessed.isoformat() if station.last_accessed else None
            ))
            await self.connection.commit()
    
    async def get_station(self, icao: str) -> Optional[StationInfo]:
        """Retrieve station information."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM stations WHERE icao = ?",
                (icao.upper(),)
            )
            row = await cursor.fetchone()
            if row:
                return StationInfo(
                    icao=row['icao'],
                    name=row['name'],
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    elevation=row['elevation'],
                    is_favorite=bool(row['is_favorite']),
                    last_accessed=datetime.fromisoformat(row['last_accessed']) if row['last_accessed'] else None
                )
            return None
    
    async def get_favorite_stations(self) -> List[StationInfo]:
        """Get all favorite stations."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM stations WHERE is_favorite = 1 ORDER BY last_accessed DESC"
            )
            rows = await cursor.fetchall()
            return [
                StationInfo(
                    icao=row['icao'],
                    name=row['name'],
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    elevation=row['elevation'],
                    is_favorite=True,
                    last_accessed=datetime.fromisoformat(row['last_accessed']) if row['last_accessed'] else None
                )
                for row in rows
            ]
    
    # User settings operations
    async def save_settings(self, settings: UserSettings):
        """Save user settings."""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO user_settings (key, value)
                VALUES ('app_settings', ?)
            """, (settings.model_dump_json(),))
            await self.connection.commit()
    
    async def get_settings(self) -> UserSettings:
        """Retrieve user settings or return defaults."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT value FROM user_settings WHERE key = 'app_settings'"
            )
            row = await cursor.fetchone()
            if row:
                return UserSettings.model_validate_json(row['value'])
            return UserSettings()  # Return defaults
    
    # Cache management
    async def clear_old_cache(self, max_age_hours: int = 24):
        """Clear cache entries older than specified hours."""
        cutoff = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM metar_cache WHERE cached_at < ?",
                (cutoff_iso,)
            )
            await cursor.execute(
                "DELETE FROM taf_cache WHERE cached_at < ?",
                (cutoff_iso,)
            )
            await cursor.execute(
                "DELETE FROM pirep_cache WHERE cached_at < ?",
                (cutoff_iso,)
            )
            await self.connection.commit()
