# IVAO Weather Tool

A cross-platform Python desktop application for understanding and using aviation weather in online ATC and virtual flight operations. It combines live FAA weather data with powerful decoding tools for IVAO controllers and pilots.

## Features

- **Live Weather Data**: Real-time METAR and TAF from FAA/NOAA sources
- **Advanced Decoding**: Full decoding of METAR and TAF including complex remarks, change groups, and runway visual ranges
- **Weather Calculator**: Integrated tools for Density Altitude, Crosswind Component, and Unit Conversions
- **Manual Decoder**: Decode any raw weather string instantly without searching for an airport
- **Flight Categories**: Visual VFR/MVFR/IFR/LIFR indicators
- **Offline Mode**: Cached weather data for offline access
- **Training Module**: Interactive lessons and quizzes (Coming Soon)
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.11 or higher
- Internet connection (for live weather data)

## Installation


### Running the Executable (Windows)
1. Navigate to the `dist` folder
2. Double-click `IVAO Weather Tool.exe`
3. No Python installation required!

### From Source

1. Clone the repository:
```bash
git clone https://github.com/cartesianpixels/ivao-weather-tool.git
cd ivao-weather-tool
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **macOS/Linux**: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Copy `.env.example` to `.env` and configure as needed:
```bash
cp .env.example .env
```

6. Run the application:
```bash
python src/main.py
```

## Development

### Project Structure

```
ivao-weather-tool/
├── src/
│   ├── data/          # Data layer (API, cache, database)
│   ├── domain/        # Business logic (decoders, calculators)
│   ├── ui/            # User interface (PySide6)
│   └── resources/     # Assets, icons, styles
├── tests/             # Unit and integration tests
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Usage

1. Launch the application
2. Search for an airport using ICAO code (e.g., KJFK)
3. View decoded weather information
4. Access training modules from the menu
5. Configure preferences in Settings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Weather data provided by FAA Aviation Weather Center
- Built for the IVAO community
- **Author**: Abdellah Chaaibi (IVAO VID: 710267)
- **Contact**: cartesianpixels@gmail.com
