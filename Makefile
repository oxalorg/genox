.PHONY: build upload release

install:
	pip install -e .

build:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

release: build upload
