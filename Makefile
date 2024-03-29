.PHONY: black flake8 flake8_test ut start

all: lint ut

lint: flake8 flake8_test black

black:
	black ./src ./tests

flake8:
	flake8 --max-line-length=100 --ignore=E203,W503 ./src

flake8_test:
	flake8 --max-line-length=100 --ignore=E203,W503 ./tests

ut:
	pytest -v --capture=no --cov-config .coveragerc --cov=src --cov-report=xml --cov-report=term-missing .

start:
	rm ./tidydir.db
	rm -rf ./tests/data-tmp
	mkdir ./tests/data-tmp
	mkdir ./tests/data-tmp/2022-12-27
	tidydir ./tests/data-org ./tests/data-tmp

