.PHONY: build upload

build:
	python3 setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*
