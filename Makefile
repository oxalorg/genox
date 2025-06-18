.PHONY: build upload release init install

init:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

install:
	venv/bin/pip install -e .

build:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

release: build upload
