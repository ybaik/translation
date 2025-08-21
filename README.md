# Translation
Python package for game translation

## Installation

### Requirements
- Python 3.9+

### Setup
1. Clone repository:
```bash
git clone git@github.com:ybaik/translation.git
cd translation
```

2. Install dependencies and package:
```bash
   pip install -e .
```

### Usage
1. Extract scripts from game data:
```bash
python extract_script_auto.py # after modifying the inputs in the script
```

2. Translate scripts:
```bash
python tools/fit_scripts.py # after modifying the inputs in the script
```

3. Patch game data:
```bash
python write_script_auto.py # after modifying the inputs in the script
```

Note: Recommended to use conda or virtual environment
