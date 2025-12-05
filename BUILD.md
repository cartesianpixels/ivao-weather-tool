# Build Instructions for IVAO Weather Tool

## Prerequisites

1. Install PyInstaller:
```bash
pip install pyinstaller
```

## Building the Executable

### Windows

1. **One-File Executable** (recommended for distribution):
```bash
pyinstaller --onefile --windowed --name "IVAO Weather Tool" src/main.py
```

2. **Using the spec file** (for more control):
```bash
pyinstaller ivao_weather_tool.spec
```

3. **With custom icon** (if you have an icon file):
```bash
pyinstaller --onefile --windowed --name "IVAO Weather Tool" --icon=icon.ico src/main.py
```

### Output

The executable will be created in:
- `dist/IVAO Weather Tool.exe` (one-file mode)
- `dist/IVAO_Weather_Tool/` (directory mode)

## Distribution Package

Create a distribution folder with:
```
IVAO_Weather_Tool_v1.0/
├── IVAO Weather Tool.exe
├── README.txt
└── LICENSE.txt
```

Then zip it for distribution.

## Build Script (Automated)

For convenience, you can use the build script:

**Windows (PowerShell)**:
```powershell
.\build.ps1
```

**Windows (Command Prompt)**:
```cmd
build.bat
```

## Troubleshooting

### Missing DLLs
If the app fails to start due to missing DLLs, use:
```bash
pyinstaller --onefile --windowed --hidden-import=PySide6 src/main.py
```

### Large File Size
To reduce executable size:
1. Use `--exclude-module` for unused packages
2. Use UPX compression (included by default)
3. Consider directory mode instead of one-file

### Testing
Always test the executable on a clean Windows machine without Python installed to ensure all dependencies are bundled.

## Version Information

To add version information to the executable (Windows only):

1. Create a `version_info.txt` file
2. Build with: `pyinstaller --version-file=version_info.txt ...`

## Code Signing (Optional)

For production releases, consider code signing the executable to avoid Windows SmartScreen warnings.

## Notes

- The first run may be slow as PyInstaller unpacks files
- Antivirus software may flag the executable (false positive)
- File size will be ~50-100MB due to bundled Python runtime and dependencies
