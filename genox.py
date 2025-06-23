import logging
import os
import shutil
import time
import json
from pathlib import Path
from datetime import date
from datetime import datetime

import markdown2
import yaml
from jinja2 import Environment, FileSystemLoader
import re

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
            raise ValueError('Invalid Hook name')

    @staticmethod
    def index_list(site, context):
        from itertools import groupby
        index_list = []
        tags = set()
        for k, page in site.items():
            page_tags = page.get('tags')
            if page_tags:
                tags.update(page_tags)
            draft = page.get('draft')
            if draft:
                continue
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
    "strike",
    "smarty-pants",
    "tables",
    "markdown-in-html",
    "link-patterns",
    # "metadata",
]

_pattern = (
    r'((([A-Za-z]{3,9}:(?:\/\/)?)'  # scheme
    r'(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+(:\[0-9]+)?'  # user@hostname:port
    r'|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)'  # www.|user@hostname
    r'((?:\/[\+~%\/\.\w\-_]*)?'  # path
    r'\??(?:[\-\+=&;%@\.\w_]*)'  # query parameters
    r'#?(?:[\.\!\/\\\w]*))?)'  # fragment
    r'(?![^<]*?(?:<\/\w+>|\/?>))'  # ignore anchor HTML tags
    r'(?![^\(]*?\))'  # ignore links in brackets (Markdown links and images)
)
LINK_PATTERNS = [(re.compile(_pattern),r'\1')]
_markdown = markdown2.Markdown(extras=_md_extras, link_patterns=LINK_PATTERNS).convert

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


def jinja_time_formatter(x, y):
    if x is not None and y is not None:
        return x.strftime(y)
    else:
        return ""

def get_jinja_renderer(layout_dir, defaults, globals={}):
    jinja_loader = FileSystemLoader(layout_dir)
    jinja_env = Environment(loader=jinja_loader)
    # jinja_env.filters['datetimeformat'] = lambda x, y: x.strftime(y)
    jinja_env.filters['datetimeformat'] = jinja_time_formatter
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
                fconfig = config['defaults'].copy()
                fconfig.update(metadata)
                fconfig.update({
                    'site': config['site'],
                    'raw_content': content,
                    'content': md2html(content),
                    'published_at': int(datetime.combine(metadata.get('date', date(1970, 1, 1)), datetime.min.time()).timestamp()) * 1000,
                    'rel_path': relfpath,
                    'rel_url': "/{}/".format(os.path.relpath(os.path.join(root, fbase), src)),
                    'container_path': os.path.relpath(root, src),
                    'images': [],
                })
                # find all images from html content
                for image in re.findall(r'<img.*?src="(.*?)".*?>', fconfig['content']):
                    fconfig['images'].append(image)
                if not fconfig.get('excerpt', None):
                    excerpt_separator = "<!--more-->"
                    fconfig['excerpt'] = ""
                    if excerpt_separator in content:
                        fconfig['excerpt'] = content.split('<!--more-->')[0].replace('\n', ' ').strip()
                    else:
                        fconfig['excerpt'] = content[:200] + "..."
                if fbase == "_index":
                    fconfig['slug'] = os.path.basename(root)
                    fconfig['is_index'] = True
                    fconfig['rel_url'] = "/{}/".format(os.path.relpath(root, src))
                else:
                    fconfig['slug'] = fbase
                    fconfig['rel_url'] = "/{}/".format(os.path.relpath(os.path.join(root, fbase), src))
                site[relfpath] = fconfig
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

def ghost_exporter(site):
    posts = []
    for path, post in site.items():
        data = {}
        if path.startswith("blog/"):
            if post.get('date'):
                data['title'] = post['title']
                data['slug'] = post['slug']
                data['status'] = "published"
                data['published_at'] = int(datetime.combine(post['date'], datetime.min.time()).timestamp()) * 1000
                data['html'] = post['content']
                posts.append(data)

    ghost = {"data": {"posts": posts}}
    with open('ghost.json', 'w', encoding='utf-8') as f:
        json.dump(ghost, f, ensure_ascii=False, indent=4)

def sitemap(site, dst):
    sitemap = []
    site_items = filter(lambda x: x[0].startswith("blog/") and not x[1].get('draft', False), site.items())
    site_items = sorted(site_items, key=lambda x: x[1]['published_at'], reverse=True)
    for path, post in site_items:
        sitemap.append({
           "url": f"{post['site']['url']}{post['rel_url']}",
        })
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in sitemap:
        xml += '  <url>\n'
        xml += f'    <loc>{page["url"]}</loc>\n'
        xml += '  </url>\n'
    xml += '</urlset>'
    with open(os.path.join(dst, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(xml)

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
    ghost_exporter(site)
    jinja_renderer = get_jinja_renderer(layout_dir, config['defaults'], globals=site)
    # print(site)
    build(site, dst, jinja_renderer)
    sitemap(site, dst)
    return site


def cli():
    logging.basicConfig(filename='.genox.log', filemode='w', level=logging.DEBUG)
    logging.info("Starting genox..")
    t_start = time.time()
    site = main()
    print("Site built in \033[43m\033[31m{:0.3f}\033[0m\033[49m seconds. That's quite fast, ain't it?".format(
        time.time() - t_start))
    # print("Built: {} pages.".format(len(oxgen.site['pages'])))
    logging.info("Finished. Exiting...")


if __name__ == '__main__':
    cli()
