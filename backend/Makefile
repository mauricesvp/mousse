all: format lint

format:
	python3 -m isort mousse/
	python3 -m black mousse/

lint:
	python3 -m isort -c mousse/
	python3 -m black --check mousse/
	python3 -m flake8 mousse/
	python3 -m mypy mousse/
