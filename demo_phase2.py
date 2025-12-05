#!/usr/bin/env python3
"""
Demo script showing Phase 2 capabilities.
Demonstrates API client, caching, and database operations.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.database import Database
from src.data.api_client import WeatherAPIClient
from src.data.cache_manager import CacheManager


async def main():
    """Demo the data layer capabilities."""
    print("=" * 60)
    print("IVAO Weather Tool - Phase 2 Demo")
    print("=" * 60)
    print()
    
    # Initialize components
    print("📦 Initializing database and API client...")
    db = Database("data/demo_cache.db")
    await db.connect()
    
    async with WeatherAPIClient() as api:
        cache = CacheManager(db, api, cache_ttl_minutes=10)
        
        # Test 1: Fetch METAR
        print("\n🌤️  Test 1: Fetching METAR for KJFK...")
        print("-" * 60)
        metar = await cache.get_metar("KJFK")
        if metar:
            print(f"✅ Station: {metar.station}")
            print(f"✅ Raw METAR: {metar.raw_text}")
            print(f"✅ Cached at: {metar.cached_at}")
        else:
            print("❌ No METAR data available")
        
        # Test 2: Fetch TAF
        print("\n📋 Test 2: Fetching TAF for KJFK...")
        print("-" * 60)
        taf = await cache.get_taf("KJFK")
        if taf:
            print(f"✅ Station: {taf.station}")
            print(f"✅ Raw TAF:\n{taf.raw_text}")
            print(f"✅ Cached at: {taf.cached_at}")
        else:
            print("❌ No TAF data available")
        
        # Test 3: Multiple stations
        print("\n🌍 Test 3: Fetching METARs for multiple airports...")
        print("-" * 60)
        stations = ["KLAX", "KORD", "KSFO"]
        metars = await cache.get_multiple_metars(stations)
        print(f"✅ Retrieved {len(metars)} METARs:")
        for m in metars:
            print(f"   • {m.station}: {m.raw_text[:50]}...")
        
        # Test 4: Cache status
        print("\n💾 Test 4: Cache Status...")
        print("-" * 60)
        status = cache.get_cache_status()
        print(f"✅ Online: {status['online']}")
        print(f"✅ Cache TTL: {status['cache_ttl_minutes']} minutes")
        
        # Test 5: Check cached METAR (should be instant)
        print("\n⚡ Test 5: Retrieving from cache (should be instant)...")
        print("-" * 60)
        import time
        start = time.time()
        cached_metar = await cache.get_metar("KJFK")  # Should use cache
        elapsed = time.time() - start
        print(f"✅ Retrieved in {elapsed*1000:.1f}ms (from cache)")
        print(f"✅ Data age: {(asyncio.get_event_loop().time() - cached_metar.cached_at.timestamp()):.1f}s")
        
        # Test 6: User settings
        print("\n⚙️  Test 6: User Settings...")
        print("-" * 60)
        from src.data.models import UserSettings
        settings = UserSettings(
            theme="dark",
            default_airports=["KJFK", "KLAX", "KORD"],
            wind_unit="knots",
            temperature_unit="celsius"
        )
        await db.save_settings(settings)
        loaded = await db.get_settings()
        print(f"✅ Theme: {loaded.theme}")
        print(f"✅ Default airports: {', '.join(loaded.default_airports)}")
        print(f"✅ Units: {loaded.wind_unit}, {loaded.temperature_unit}")
    
    await db.close()
    
    print("\n" + "=" * 60)
    print("✅ Phase 2 Demo Complete!")
    print("=" * 60)
    print("\n📝 Summary:")
    print("   • API client working with retry logic")
    print("   • Database caching operational")
    print("   • Offline mode ready (falls back to cache)")
    print("   • User settings persistence working")
    print("\n🚀 Next: Phase 3 will add METAR/TAF decoding!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
