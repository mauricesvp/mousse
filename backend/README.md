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

## MySQL CLI
Do you want to inspect the database manually? Do this:

0. Make sure the mysql service is running.
1. `$ sudo docker exec -it mousse_mysql_1 /bin/bash`
2. (Inside docker:) mysql --password moussedb
3. Enter `root`
4. (Inside MySQL monitor:) `use moussedb;`
5. You are good to go! Try `select count(*) from modules;`

## TODOS
* Add sanity check before exporting data
* Periodically delete data from database (e.g. TTL)
* Add tests
