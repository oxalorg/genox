import logging
import os
import shutil
import time

import markdown2
import yaml
from jinja2 import Environment, FileSystemLoader


def extract_yaml(text):
    """
    Extracts YAML metadata block from the top of the
    text, and returns it along with the remaining text.
    """
    first_line = True
    metadata = []
    content = []
    metadata_parsed = False

    for line in text.split('\n'):
        if first_line:
            first_line = False
            if line.strip() != '---':
                raise MetaParseException('Invalid metadata')
        elif line.strip() == '' and not metadata_parsed:
            pass
        elif line.strip() == '---' and not metadata_parsed:
            # reached the last line
            metadata_parsed = True
        elif not metadata_parsed:
            metadata.append(line)
        else:
            content.append(line)

    try:
        content = '\n'.join(content)
        metadata = yaml.load('\n'.join(metadata))
        metadata = metadata or {}
    except:
        raise

    return metadata, content


# Markdown to html conversions
_md_extras = [
    "code-friendly",
    "fenced-code-blocks",
    "footnotes",
    "header-ids",
    "markdown-in-html",
    # "metadata",
]
_markdown = markdown2.Markdown(extras=_md_extras).convert


def md2html(md):
    return _markdown(md)


def dir_ignored(directory, ignore_patterns):
    return any(os.path.basename(directory).startswith(y) for y in ignore_patterns)


def rebuild_tree_hardlinks(src, dst, ignore_ext):
    os.makedirs(dst, exist_ok=True)
    shutil.rmtree(dst)
    shutil.copytree(src, dst, copy_function=os.link, ignore=shutil.ignore_patterns(*['*' + ext for ext in ignore_ext]))


def get_jinja_renderer(layout_dir, defaults):
    jinja_loader = FileSystemLoader(layout_dir)
    jinja_env = Environment(loader=jinja_loader)
    jinja_env.filters['datetimeformat'] = lambda x, y: x.strftime(y)
    jinja_env.globals = {}

    def renderer(layout, context):
        t = jinja_env.get_template(layout)
        return t.render(context)

    return renderer


def render(src, dst, context, renderer):
    layout = context.get('layout')
    if not layout.endswith('.html'):
        layout += '.html'
    if os.path.isfile(dst):
        print("A file already exists at the destination: ", dst)
        print("Skipping src file: ", src, " to prevent overwriting.")
        return
    with open(dst, 'w') as fp:
        logging.info("Writing to file: {}".format(dst))
        fp.write(renderer(layout, context))


def index(directory, md_ext, config):
    site = {}
    src = config['input_dir']
    for root, dirs, files in os.walk(directory):
        # if dir_ignored(root):
        #     print("Ignoring directory: ", root)
        #     continue

        for fname in files:
            fpath = os.path.join(root, fname)
            relfpath = os.path.relpath(fpath, src)
            fbase, fext = os.path.splitext(fname)

            if fext in md_ext:
                try:
                    metadata, content = extract_yaml(open(fpath).read())
                except:
                    print("Skipping file with invalid metadata: ", fpath)
                    continue
                site[relfpath] = config['defaults'].copy()
                site[relfpath].update(metadata)
                site[relfpath]['content'] = content

    return site


def build(site, dst, renderer):
    for fpath, context in site.items():
        # convert content to html
        context['content'] = md2html(context['content'])
        slug = context.get('slug', None)
        if slug:
            out_fpath = os.path.join(os.path.basename(fpath), slug)
        else:
            out_fpath = fpath
        out_fpath = os.path.join(dst, out_fpath)
        out_fpath = os.path.splitext(out_fpath)[0] + '.html'
        render(fpath, out_fpath, context, renderer)


def main():
    config = yaml.load(open('config.yml').read())
    src, dst, layout_dir, md_ext = config['input_dir'], config['output_dir'], config['layout_dir'], config['md_ext']
    rebuild_tree_hardlinks(src, dst, md_ext)
    jinja_renderer = get_jinja_renderer(layout_dir, config['defaults'])
    site = index(src, md_ext, config)
    print(site)
    build(site, dst, jinja_renderer)


def cli():
    logging.basicConfig(filename='.oxgen.log', filemode='w', level=logging.DEBUG)
    logging.info("Starting oxgen..")
    t_start = time.time()
    main()
    print("Site built in \033[43m\033[31m{:0.3f}\033[0m\033[49m seconds. That's quite fast, ain't it?".format(
        time.time() - t_start))
    # print("Built: {} pages.".format(len(oxgen.site['pages'])))
    logging.info("Finished. Exiting...")


if __name__ == '__main__':
    cli()
