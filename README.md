# genox - extremely simple static site generator

Because simplicity is a virtue.

## Why yet another static site generator?

I've used Jekyll, Hugo, Gatsby, Pelican, and countless other
static site generators for multiple websites.

I've disliked every single one of them.

* Some are too simple, and some are way too complex.
* Some have incomplete docs, some have complex docs.
* Some are opiniated, some are way too barebones.

Genox is my solution to my painpoints in dealing with other
SSGs.

## Philosophy

TODO

## Directory Structure

TODO

## Config

TODO

## Features

TODO

## Hooks

TODO

## Installation

Simply copy `genox.py`, `requirements.txt` and `config.yml` in
to your project directory. 

Create a virtualenv (or not) and install the requirements.

```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Then run 

```
python3 genox.py
```

I won't be uploading it to pypi, because this is not meant to be installed -
it's meant to be forked (the real reason is I am lazy and python doesn't
make it easy to publish packages). The code is very small, easy to read. Just
fork this repository in your website root and start hacking.

All "site" specific configurations are handled in `config.yml` file (must be
present in the same directory as `genox.py`), everything else can be
customized.
