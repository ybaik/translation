# Translation Toolkit

A modern Python package for reverse engineering and translating Japanese video games into Korean.

## Features
- **Script Extraction**: Extract Japanese text from binary files with font table support.
- **Script Injection**: Inject translated Korean text back into game binaries.
- **Font Management**: Handle custom font tables (.tbl, .json) and font image generation.
- **Encoding Support**: Built-in support for common encoding/decoding schemes (e.g., XOR).
- **Name Database**: Manage character names for consistent translation.

## Installation

### Requirements
- Python 3.9+

### Setup
1. Clone the repository:
   ```bash
   git clone git@github:ybaik/translation.git
   cd translation
   ```

2. Install in editable mode with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Usage

### 1. Extract Scripts
Extract Japanese text from game data:
```bash
python extract_script_auto.py
```

### 2. Translate
Translate the extracted JSON (e.g., `S01_VIS_jpn.json`) to Korean (e.g., `S01_VIS_kor.json`).

### 3. Patch Game Data
Inject the translated script back into the binary:
```bash
python write_script_auto.py
```

## Project Structure
- `module/`: Core library (Script, FontTable, etc.)
- `tools/`: Utility scripts for translation and conversion.
- `font_table/`: Predefined font tables for various platforms.
- `name_db/`: Databases for consistent character name translation.

## License
MIT License
