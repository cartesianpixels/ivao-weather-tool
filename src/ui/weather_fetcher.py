"""
Weather fetcher worker thread for IVAO Weather Tool.
"""

from PySide6.QtCore import QThread, Signal
import asyncio
from src.data.api_client import WeatherAPIClient, WeatherAPIError
from src.domain.metar_decoder import MetarDecoder
from src.domain.taf_decoder import TafDecoder

class WeatherFetcher(QThread):
    """Worker thread to fetch weather data asynchronously."""
    
    # Signals
    weather_ready = Signal(object, object)  # (metar_data, taf_data)
    error_occurred = Signal(str)  # error message
    
    def __init__(self, airport_code: str):
        """Initialize fetcher."""
        super().__init__()
        self.airport_code = airport_code
        self.metar_decoder = MetarDecoder()
        self.taf_decoder = TafDecoder()
        
    def run(self):
        """Fetch weather data in background thread."""
        try:
            # Run async code in this thread
            asyncio.run(self._fetch_weather())
        except Exception as e:
            self.error_occurred.emit(str(e))
            
    async def _fetch_weather(self):
        """Async function to fetch and decode weather."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            async with WeatherAPIClient() as client:
                # Fetch METAR
                metars = await client.get_metar([self.airport_code])
                if not metars:
                    self.error_occurred.emit(f"No METAR data found for {self.airport_code}")
                    return
                    
                # Decode METAR
                try:
                    metar_data = self.metar_decoder.decode(metars[0], self.airport_code)
                except Exception as e:
                    logger.error(f"Failed to decode METAR for {self.airport_code}: {e}")
                    self.error_occurred.emit(f"Error decoding METAR: {str(e)}")
                    return
                
                # Fetch TAF
                taf_data = None
                try:
                    tafs = await client.get_taf([self.airport_code])
                    if tafs:
                        logger.info(f"Retrieved TAF for {self.airport_code}: {tafs[0][:100]}...")
                        taf_data = self.taf_decoder.decode(tafs[0], self.airport_code)
                        logger.info(f"Successfully decoded TAF for {self.airport_code}")
                    else:
                        logger.info(f"No TAF available for {self.airport_code}")
                except Exception as e:
                    # TAF might not be available for all airports
                    logger.warning(f"TAF fetch/decode failed for {self.airport_code}: {e}")
                    # Continue without TAF - this is not a fatal error
                    
                # Always emit results, even if TAF is None
                self.weather_ready.emit(metar_data, taf_data)
                
        except WeatherAPIError as e:
            logger.error(f"API Error for {self.airport_code}: {e}")
            self.error_occurred.emit(f"API Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error for {self.airport_code}: {e}")
            self.error_occurred.emit(f"Error: {str(e)}")
