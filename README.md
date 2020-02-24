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

```
# The directory where actual content stays
input_dir: content

# The directory where our jinja templates stay
layout_dir: layouts

# The directory where our static files (assets) stay
# eg. css, js, images, etc.
# We want to place files in static directory which do not need
# to be processed.
static_dir: static

# The final produced site goes in there.
output_dir: _build

# these are the default values used for file-specific
# configuration
defaults:
    layout: post
    author: ox
    author_link: https://oxal.org

# these are site-specific values available under the
# config['site'] variable or {{ site }} in templates
# tl;dr these are user customizable config values
site:
    title: "genox - such k00l much w0w"
    description: "Now this is the story all about how my site got flipped..."
    google_analytics_id: "GA-WOW"

# markdown extension you want to process
md_ext:
  - '.md'
  - '.mkd'
  - '.markdown'
  - '.rst' # rst is not supported but maybe your markdown files end with rst?
```

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
