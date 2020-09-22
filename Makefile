.PHONY: build upload release

build:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

release: build upload
