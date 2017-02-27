# genox - extremely simple static site generator

This is not a library. This is not a framework.
I hate coding logic in the templating languages,
but that is what every other static site generator
seems to be doing. So this is my way of coding
in python and letting the templating language
only act as presentation.

I won't be uploading it to pypi, because this is not
meant to be installed - it's meant to be forked.
The code is very small, easy to read. Just fork
this repository in your website root and start hacking.

All "site" specific configurations are handled in
`config.yml` file (must be present in the same directory
as `oxgen.py`), everything else can be customized.
