# IVAO Weather Tool - User Guide

## Quick Start

1. **Launch** the application by double-clicking `IVAO Weather Tool.exe`
2. **Enter** an airport ICAO code in the search box (e.g., KJFK, EGLL, LFPG)
3. **View** the decoded weather information

That's it! The app will fetch and decode the latest METAR and TAF for your airport.

## Features

### Weather Display
- **METAR**: Current weather observation with full decoding
- **TAF**: Terminal Aerodrome Forecast with all change groups
- **Flight Category**: Color-coded VFR/MVFR/IFR/LIFR indicator
- **Interpretation**: Plain language explanation of weather conditions

### Tools

#### Weather Calculator
Access from toolbar or press `Ctrl+K`

**Density Altitude**:
- Calculate density altitude for performance planning
- Input pressure altitude, temperature, and dewpoint
- Get results in feet

**Crosswind Component**:
- Calculate headwind and crosswind components
- Input runway heading and wind data
- Useful for landing calculations

**Unit Conversions**:
- Temperature: Celsius ↔ Fahrenheit
- Pressure: inHg ↔ hPa
- Speed: Knots ↔ MPH ↔ KPH
- Distance: Statute Miles ↔ Kilometers

#### Manual Decoder
Access from toolbar or press `Ctrl+M`

- Paste any METAR or TAF text
- Get instant decoding
- No need to search for airport
- Perfect for training or studying

### Settings
Access from toolbar or press `Ctrl+,`

**Display**:
- Theme: Dark or Light mode
- Wind units: Knots or MPH
- Temperature: Celsius or Fahrenheit
- Pressure: inHg or hPa

**Updates**:
- Auto-refresh interval (future feature)
- Cache duration

**Airports**:
- Manage favorite airports (future feature)

### View Menu

**Toggle Calculator**: Show/hide calculator window
**Toggle Status Bar**: Show/hide status bar
**Font Size**: Small, Medium, or Large
**Reset Layout**: Reset window to default size

## Understanding the Display

### Flight Categories

- **VFR** (Green): Visual Flight Rules - Good conditions
  - Ceiling ≥ 3000 ft AND Visibility ≥ 5 SM

- **MVFR** (Blue): Marginal VFR - Acceptable conditions
  - Ceiling 1000-3000 ft OR Visibility 3-5 SM

- **IFR** (Red): Instrument Flight Rules - Poor conditions
  - Ceiling 500-1000 ft OR Visibility 1-3 SM

- **LIFR** (Magenta): Low IFR - Very poor conditions
  - Ceiling < 500 ft OR Visibility < 1 SM

### METAR Components

**Example**: `KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012`

- `KJFK` - Airport code
- `041651Z` - Date (4th) and time (16:51 UTC)
- `31008KT` - Wind from 310° at 8 knots
- `10SM` - Visibility 10 statute miles
- `FEW250` - Few clouds at 25,000 feet
- `04/M03` - Temperature 4°C, Dewpoint -3°C
- `A3012` - Altimeter 30.12 inHg

### TAF Components

**Change Indicators**:
- `FM` (From): Permanent change starting at specified time
- `TEMPO` (Temporary): Temporary fluctuations (< 1 hour)
- `BECMG` (Becoming): Gradual change over time period
- `PROB` (Probability): Probability of conditions occurring

## Tips & Tricks

1. **Recent Searches**: The app remembers your searches (future feature)
2. **Offline Mode**: Previously viewed weather is cached for offline access
3. **Copy Text**: Right-click to copy decoded weather text (future feature)
4. **Multiple Windows**: Open calculator and manual decoder simultaneously
5. **Theme**: Dark mode reduces eye strain in low-light environments

## Troubleshooting

### App Won't Start
- Ensure you have Windows 10 or later
- Check antivirus isn't blocking the app
- Try running as administrator

### No Weather Data
- Check your internet connection
- Verify the ICAO code is correct (4 letters)
- Some small airports may not have TAF data

### Slow Performance
- Close other applications
- Check available disk space
- Restart the application

### Windows SmartScreen Warning
- Click "More info"
- Click "Run anyway"
- This is normal for unsigned applications

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open Calculator |
| `Ctrl+M` | Open Manual Decoder |
| `Ctrl+,` | Open Settings |
| `Ctrl+Q` | Quit Application |
| `F5` | Refresh current weather |

## Support

**Found a bug?** Report it on GitHub
**Have a question?** Ask on IVAO forums
**Want a feature?** Submit a feature request

## Credits

Weather data provided by FAA Aviation Weather Center
Built for the IVAO community

---

**Version**: 1.0.0
**Last Updated**: December 5, 2025
