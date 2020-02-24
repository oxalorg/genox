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

## Config

All config is stored in `config.yml` file. It needs to be in the
same directory as `genox.py` which is considered the root
directory.

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

## How genox builds the site?

There is no default directory structure. The specific names are
configurable in the config.yml file.

Structure for our `input_dir` is a little opiniated.

Genox will recurse into all directories and map it exactly the
same in the output site. While roaming through the input dir, it
will check for all markdown files (specified using `md_ext`
config).

It will then process each markdown file expecting them to be in
a format like this:

```
---
title: "Markdown title"
date: 2020-02-20
myvar: myvalue
hooks:
    - hook1
    - hook2
---

This is my blog post.

## Heading 2

Anything in this part of the markdown file will be available
to our templates as the {{ content }} variable and be rendered
as markdown content

```

So for example I can have a file in my `input_dir` as follows:

```
input_dir/about.md
```

and it will be available in our website at `site.com/about/`

Please note the trailing slash. What genox will do is create the
output file in a structure as follows:

```
output_dir/about/index.html
```

### What about subdirectories?

Any subdirectory will be automatically be created in output
site.

For example:

```
/input_dir/about/ox.md

|
v

/output_dir/about/ox/index.html

|
v

site.com/about/ox/
```

But what if now you also want to put something at
`site.com/about/`

This is where we use a special file called `_index.md`

```
/input_dir/about/_index.md
/input_dir/about/ox.md
/input_dir/about/sakura/_index.md
/input_dir/about/sakura/photo.jpg

|
v

/output_dir/about/index.html
/output_dir/about/ox/index.html
/output_dir/about/sakura/index.html
/output_dir/about/sakura/photo.jpg

|
v

site.com/about/
site.com/about/ox/
site.com/about/sakura/
site.com/about/sakura/photo.jpg

```

All non markdown files will be copied to output site preserving
the directory structure.

What if we want to access a list of people in the about
directory in the `about/_index.md` i.e. basically we want to
create an index page.

Well customizations like this is where `hooks` come in. Read
more below.

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

