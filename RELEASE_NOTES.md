# IVAO Weather Tool - Release v1.0.0

## Release Notes

### Version 1.0.0 - Initial Release
**Release Date**: December 5, 2025

### Features

#### Core Functionality
- ✅ **Live Weather Data** - Real-time METAR and TAF from FAA/NOAA Aviation Weather Center
- ✅ **Offline Support** - Cached weather data with SQLite database
- ✅ **Weather Decoding** - Complete METAR and TAF interpretation
- ✅ **Flight Categories** - Visual VFR/MVFR/IFR/LIFR indicators with color coding
- ✅ **Human-Readable Explanations** - Plain language weather interpretations

#### Tools
- ✅ **Weather Calculator** - Density altitude, crosswind components, unit conversions
- ✅ **Manual Decoder** - Paste and decode any METAR or TAF
- ✅ **Search History** - Quick access to recently viewed airports

#### User Interface
- ✅ **Dark Mode** - Professional dark theme (default)
- ✅ **Light Mode** - Clean light theme alternative
- ✅ **Responsive Design** - Adapts to different window sizes
- ✅ **Keyboard Shortcuts** - Quick access to all features

#### Settings
- ✅ **Unit Preferences** - Customize wind, temperature, and pressure units
- ✅ **Theme Selection** - Switch between dark and light modes
- ✅ **Default Airports** - Set favorite airports for quick access

### Technical Details

**Built With**:
- Python 3.11+
- PySide6 (Qt for Python)
- HTTPX for API requests
- Pydantic for data validation
- SQLite for local caching

**Supported Platforms**:
- Windows 10/11 (64-bit)
- macOS 10.15+ (planned)
- Linux (planned)

### Installation

#### Windows
1. Download `IVAO_Weather_Tool_v1.0.0_Windows.zip`
2. Extract the ZIP file
3. Run `IVAO Weather Tool.exe`
4. No installation required!

### System Requirements

**Minimum**:
- Windows 10 or later
- 4 GB RAM
- 200 MB disk space
- Internet connection (for live weather data)

**Recommended**:
- Windows 11
- 8 GB RAM
- SSD storage
- Broadband internet

### Known Issues

1. **First Launch**: May take a few seconds to start as files are unpacked
2. **Antivirus**: Some antivirus software may flag the executable (false positive)
3. **Windows SmartScreen**: May show warning on first run (click "More info" → "Run anyway")

### Usage

1. **Search for Weather**: Enter ICAO airport code (e.g., KJFK, EGLL, LFPG)
2. **View Decoded Data**: See complete METAR and TAF interpretation
3. **Use Calculator**: Access weather calculations from toolbar
4. **Manual Decode**: Paste any METAR/TAF for instant decoding
5. **Customize**: Change theme and units in Settings

### Keyboard Shortcuts

- `Ctrl+K` - Open Calculator
- `Ctrl+M` - Open Manual Decoder
- `Ctrl+,` - Open Settings
- `Ctrl+Q` - Quit Application

### What's Next?

**Planned for v1.1.0**:
- PIREP support
- Training module with interactive lessons
- Multiple airport comparison
- Weather alerts and notifications
- Export to PDF/text

**Planned for v2.0.0**:
- Mobile app (iOS/Android)
- Cloud sync for settings
- Collaborative features
- Advanced weather charts

### Support

**Issues**: Report bugs on GitHub
**Questions**: Contact via IVAO forums
**Updates**: Check GitHub releases for new versions

### Credits

- **Weather Data**: FAA Aviation Weather Center
- **Built for**: IVAO Community
- **Author**: Abdellah Chaaibi (IVAO VID: 710267) <cartesianpixels@gmail.com>

### License

MIT License

---

## Changelog

### v1.0.0 (2025-12-05)
- Initial release
- METAR/TAF decoding
- Weather calculator
- Manual decoder
- Dark/Light themes
- Settings management
- Offline caching
