import logging
import os
import shutil
import time
import json
from pathlib import Path

import yaml
import markdown2
from jinja2 import Environment, FileSystemLoader


GENOX_IGNORE_LIST = {}

class MetaParseException(ValueError):
    pass


class GenHook:
    @staticmethod
    def after_config_read(config):
        DEBUG = os.getenv("DEBUG", False)
        config["DEBUG"] = DEBUG

        manifest_file_name = config.get("manifest_file_name", None)
        if manifest_file_name and os.path.isfile(manifest_file_name):
            config["manifest"] = json.load(open(manifest_file_name))


    def call_hook(hook_name, site, context):
        func = getattr(GenHook, hook_name)
        if func:
            func(site, context)
        else:
            logging.info('Invalid Hook name')

    @staticmethod
    def index_list(site, context):
        from itertools import groupby
        index_list = []
        tags = set()
        for k, page in site.items():
            page_tags = page.get('tags')
            if page_tags:
                tags.update(page_tags)
            if k.startswith(context['container_path']) and k != context['rel_path']:
                index_list.append(site[k])

        index_list.sort(key=lambda x: x['date'], reverse=True)

        index_group = {}
        for k, it in groupby(index_list, lambda x: x['date'].year):
            index_group[k] = list(it)

        context['index_list'] = index_list
        context['tags'] = tags
        context['index_group'] = index_group


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
        metadata = yaml.load('\n'.join(metadata), Loader=yaml.FullLoader)
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
    "strike",
    "smarty-pants",
    "tables",
    # "metadata",
]
_markdown = markdown2.Markdown(extras=_md_extras).convert


def md2html(md):
    return _markdown(md)


def dir_ignored(directory, ignore_patterns):
    return any(os.path.basename(directory).startswith(y) for y in ignore_patterns)


def genox_ignored(relpath):
    return relpath in GENOX_IGNORE_LIST


def rebuild_tree_hardlinks(src, dst, static_dir, ignore_ext):
    os.makedirs(dst, exist_ok=True)
    shutil.rmtree(dst)
    shutil.copytree(src, dst, copy_function=os.link, ignore=shutil.ignore_patterns(*['*' + ext for ext in ignore_ext]))
    shutil.copytree(static_dir, os.path.join(dst, static_dir), copy_function=os.link)


def get_jinja_renderer(layout_dir, defaults, globals={}):
    jinja_loader = FileSystemLoader(layout_dir)
    jinja_env = Environment(loader=jinja_loader)
    jinja_env.filters['datetimeformat'] = lambda x, y: x.strftime(y)
    jinja_env.globals = globals

    def renderer(layout, context):
        t = jinja_env.get_template(layout)
        return t.render(context)

    return renderer


def render(src, dst, context, renderer):
    layout = context.get('layout')
    if not layout.endswith('.html'):
        layout += '.html'
    if os.path.isfile(dst):
        logging.info(f"A file already exists at the destination: {dst}")
        logging.info(f"Skipping src file: {src} to prevent overwriting.")
        return
    # make directories
    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, 'w') as fp:
        logging.info("Writing to file: {}".format(dst))
        fp.write(renderer(layout, context))


def index(directory, md_ext, config):
    site = {"_config": config}
    src = config['input_dir']
    for root, dirs, files in os.walk(directory, topdown=True):
        if genox_ignored(root):
            logging.info(f"Ignoring directory: {root}")
            # Ignoring all subdirectories also
            dirs[:] = []
            continue

        for fname in files:
            fpath = os.path.join(root, fname)
            relfpath = os.path.relpath(fpath, src)
            if genox_ignored(fpath):
                logging.info(f"Ignoring file: {fpath}")
                continue
            fbase, fext = os.path.splitext(fname)

            if fext in md_ext:
                try:
                    metadata, content = extract_yaml(open(fpath).read())
                except:
                    logging.info(f"Skipping file with invalid metadata: {fpath}")
                    continue
                site[relfpath] = config['defaults'].copy()
                site[relfpath].update(metadata)
                site[relfpath]['site'] = config['site']
                site[relfpath]['raw_content'] = content
                site[relfpath]['content'] = md2html(content)
                site[relfpath]['rel_path'] = relfpath
                site[relfpath]['rel_url'] = "/{}/".format(os.path.relpath(os.path.join(root, fbase), src))
                site[relfpath]['container_path'] = os.path.relpath(root, src)
                if fbase == "_index":
                    site[relfpath]['slug'] = os.path.basename(root)
                    site[relfpath]['is_index'] = True
                    site[relfpath]['rel_url'] = "/{}/".format(os.path.relpath(root, src))
                else:
                    site[relfpath]['slug'] = fbase
                    site[relfpath]['rel_url'] = "/{}/".format(os.path.relpath(os.path.join(root, fbase), src))
    return site


def build(site, dst, renderer):
    for fpath, context in site.items():
        if fpath == "_config":
            continue
        slug = context.get('slug', None)
        container_path = context.get('container_path')
        output_fpath = os.path.join(dst, container_path)
        if context.get('is_index', None):
            output_fpath = os.path.join(output_fpath, "index.html")
        else:
            output_fpath = os.path.join(output_fpath, slug)
            output_fpath = os.path.join(output_fpath, "index.html")
        logging.info("Rendering: {}".format(output_fpath))
        hooks = context.get('hooks', None)
        if hooks:
            logging.info(hooks)
            for hook_name in hooks:
                GenHook.call_hook(hook_name, site, context)
        render(fpath, output_fpath, context, renderer)


def main():
    config = yaml.load(open('config.yml').read(), Loader=yaml.FullLoader)
    GenHook.after_config_read(config)
    src, dst, layout_dir, md_ext = config['input_dir'], config['output_dir'], config['layout_dir'], config['md_ext']
    global GENOX_IGNORE_LIST
    try:
        with open('.genoxignore', 'r') as fp:
            GENOX_IGNORE_LIST = fp.read().splitlines()
    except FileNotFoundError:
        logging.info(".genoxignore file not found")

    static_dir = config['static_dir']
    rebuild_tree_hardlinks(src, dst, static_dir, md_ext)
    site = index(src, md_ext, config)
    jinja_renderer = get_jinja_renderer(layout_dir, config['defaults'], globals=site)
    build(site, dst, jinja_renderer)
    return site


def cli():
    logging.basicConfig(filename='.genox.log', filemode='w', level=logging.DEBUG)
    logging.info("Starting genox..")
    t_start = time.time()
    site = main()
    print("Site built in \033[43m\033[31m{:0.3f}\033[0m\033[49m seconds. That's quite fast, ain't it?".format(
        time.time() - t_start))
    logging.info("Finished. Exiting...")


if __name__ == '__main__':
    cli()
