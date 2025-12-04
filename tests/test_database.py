import pytest
import pytest_asyncio
import asyncio
from datetime import datetime
from pathlib import Path
import tempfile

from src.data.database import Database
from src.data.models import MetarData, TafData, StationInfo, UserSettings


@pytest_asyncio.fixture
async def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path))
        await db.connect()
        yield db
        await db.close()


@pytest.mark.asyncio
async def test_database_creation(temp_db):
    """Test database and tables are created."""
    assert temp_db.connection is not None
    
    # Check that tables exist
    async with temp_db.connection.cursor() as cursor:
        await cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = await cursor.fetchall()
        table_names = [t['name'] for t in tables]
        
        assert 'metar_cache' in table_names
        assert 'taf_cache' in table_names
        assert 'stations' in table_names
        assert 'user_settings' in table_names


@pytest.mark.asyncio
async def test_save_and_get_metar(temp_db):
    """Test saving and retrieving METAR."""
    metar = MetarData(
        station="KJFK",
        observation_time=datetime(2025, 12, 4, 16, 51),
        raw_text="KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012",
        flight_category="VFR"
    )
    
    await temp_db.save_metar(metar)
    
    retrieved = await temp_db.get_metar("KJFK")
    assert retrieved is not None
    assert retrieved.station == "KJFK"
    assert retrieved.raw_text == metar.raw_text
    assert retrieved.flight_category == "VFR"


@pytest.mark.asyncio
async def test_save_and_get_taf(temp_db):
    """Test saving and retrieving TAF."""
    taf = TafData(
        station="KJFK",
        issue_time=datetime(2025, 12, 4, 16, 0),
        valid_from=datetime(2025, 12, 4, 18, 0),
        valid_to=datetime(2025, 12, 5, 18, 0),
        raw_text="TAF KJFK 041600Z 0418/0518 31010KT P6SM FEW250"
    )
    
    await temp_db.save_taf(taf)
    
    retrieved = await temp_db.get_taf("KJFK")
    assert retrieved is not None
    assert retrieved.station == "KJFK"
    assert retrieved.raw_text == taf.raw_text


@pytest.mark.asyncio
async def test_save_and_get_station(temp_db):
    """Test saving and retrieving station info."""
    station = StationInfo(
        icao="KJFK",
        name="John F Kennedy International Airport",
        latitude=40.6398,
        longitude=-73.7789,
        elevation=13,
        is_favorite=True
    )
    
    await temp_db.save_station(station)
    
    retrieved = await temp_db.get_station("KJFK")
    assert retrieved is not None
    assert retrieved.icao == "KJFK"
    assert retrieved.name == station.name
    assert retrieved.is_favorite


@pytest.mark.asyncio
async def test_get_favorite_stations(temp_db):
    """Test retrieving favorite stations."""
    stations = [
        StationInfo(icao="KJFK", is_favorite=True),
        StationInfo(icao="KLAX", is_favorite=True),
        StationInfo(icao="KORD", is_favorite=False)
    ]
    
    for station in stations:
        await temp_db.save_station(station)
    
    favorites = await temp_db.get_favorite_stations()
    assert len(favorites) == 2
    assert all(s.is_favorite for s in favorites)


@pytest.mark.asyncio
async def test_save_and_get_settings(temp_db):
    """Test saving and retrieving user settings."""
    settings = UserSettings(
        theme="light",
        wind_unit="mph",
        default_airports=["KLAX", "KSFO"]
    )
    
    await temp_db.save_settings(settings)
    
    retrieved = await temp_db.get_settings()
    assert retrieved.theme == "light"
    assert retrieved.wind_unit == "mph"
    assert "KLAX" in retrieved.default_airports


@pytest.mark.asyncio
async def test_get_settings_defaults(temp_db):
    """Test getting default settings when none exist."""
    settings = await temp_db.get_settings()
    assert settings.theme == "dark"  # Default value
    assert settings.wind_unit == "knots"  # Default value
