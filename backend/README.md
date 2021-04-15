# mousse backend
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Use python3.8 or newer if possible (older versions are not tested).

## Installation
(Optional: Create and Activate a virtual environment)
```bash
python3 -m venv .venv
. .venv/bin/activate
```

To install, run
```bash
pip install -r requirements.txt
pip install .
```

## Contributing
Make sure to install the dev dependencies:
```bash
pip install -r dev-requirements.txt
```

Run formatting and linting before you commit to catch errors early and ensure a consistent code style:
```bash
make
```
