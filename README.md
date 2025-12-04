# IVAO Weather Tool

A cross-platform Python desktop application for understanding and using aviation weather in online ATC and virtual flight operations, combining live FAA weather data with structured training for IVAO controllers and pilots.

## Features

- **Live Weather Data**: Real-time METAR, TAF, PIREP from FAA/NOAA sources
- **Offline Mode**: Cached weather data for offline access
- **Weather Decoding**: Human-readable interpretation of aviation weather
- **Flight Categories**: Visual VFR/MVFR/IFR/LIFR indicators
- **Training Module**: Interactive lessons and quizzes for weather interpretation
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.11 or higher
- Internet connection (for live weather data)

## Installation

### From Source

1. Clone the repository:
```bash
git clone <repository-url>
cd WX
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

[To be determined]

## Acknowledgments

- Weather data provided by FAA Aviation Weather Center
- Built for the IVAO community
