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

- Follow the Zen of Python, as close as possible.
- Code over configuration.
- Forkable.
- Keep it simple. Reeeeeeeeeeeealy simple.

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

# manifest file used for reading dynamic static bundles from the js world
manifest_file_name: "manifest.json"
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

## Hooks

TODO

## Installation

Installing `genox` from pypi is as simple as:

```
pip3 install genox
```


This installs a script named `genox` which can be used directly on
the command line:

```
cd ~/www/oxal.org/
genox
# ^this should give you an error as we have not yet added a config.yml file
```

Now copy `config.yml` from this repo in to your project directory.

Originally genox was meant to be forked (the real reason is I am lazy and python doesn't
make it easy to publish packages). The code is very small, easy to read. Just
fork this repository in your website root and start hacking.

But I got fedup of cloning genox on different systems, and decided to set it up on pypi anyways.

## Moar Features

### Manifest - Integration with Node ecosystem

To be able to integrate genox with javascript ecosystem which bundle css/js files into bundles,
we use a manifest file. The file with `manifest_file_name` must be preset in project root. It will be read
and be available in the `{{ _config.manifest }}` template variable.

### Debug

When `DEBUG` environment variable is set to `1`, a debug flag is set which
can be accessed using `{{ _config.DEBUG }}` template variable.

```
$ DEBUG=1 genox
```

Example of Manifest and Debug - Here during development we use `out.css` as is.
But for production our asset pipeline could be producing a `hashed` file (eg:
`out.Has7d6h3Jdesa.css` which gets written to the manifest file by our node builder.

Genox can then read that file from the manifest and use it in template.

```
  {% if _config.DEBUG %}
  <link href="/static/bundle/out.css" rel="stylesheet">
  {% else %}
  <link href="/static/bundle/{{ _config.manifest["out.css"] }}" rel="stylesheet">
  {% endif %}
```

## Production Deployment

### Nginx

Here is a sample nginx location block to serve sites built using genox

```
    location / {
        root /srv/site.com/{{ build_dir }};
        index index.html index.htm;
        autoindex off;
        add_header Last-Modified $date_gmt;
        add_header Cache-Control 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0';
        if_modified_since off;
        expires off;
        etag off;
        try_files $uri $uri/ $uri.html =404;
    }
```

## Moar

### vim plugin

Genox comes with it's very own, very bad, unsuable vim-plugin!

Check it out here: https://github.com/oxalorg/vim-genox

## Share some <3

 > “Pare down to the essence, but don't remove the poetry.” ― Leonard Koren

 Please leave a star :)
