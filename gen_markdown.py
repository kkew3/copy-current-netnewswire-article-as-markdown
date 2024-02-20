import os
import json
from pathlib import Path

from lxml import etree

import convert_html


def get_data_json():
    cachedir = Path(os.environ['alfred_workflow_cache'])
    cachedir.mkdir(exist_ok=True)
    return cachedir / 'curr_data.json'


def request_convert_html(html, url):
    parser = etree.HTMLParser(
        target=convert_html.KeepOnlySupportedTarget(True))
    elements = etree.HTML(html, parser)
    opts = {'try_make_highest_header_hn': 1}
    return convert_html.StackMarkdownGenerator(opts, elements, url).generate()


def generate_article(article_data: dict):
    md = request_convert_html(article_data['html'], article_data['link'])
    link = article_data['link']
    author = ' and '.join(article_data['authors'])
    published = article_data['date']
    title = article_data['title']

    return f'''\
---
title: {title}
link: {link}
author: {author}
published: {published}
tags: []
---

{md}
'''


def write_response(arg, variables):
    print(
        json.dumps({
            'alfredworkflow': {
                'arg': arg,
                'variables': variables,
            },
        }),
        end='')


def main():
    data_json = get_data_json()
    with open(data_json, encoding='utf-8') as infile:
        article_data = json.load(infile)
    try:
        arg = generate_article(article_data)
        variables = {'err': ''}
    except Exception as err:
        err_msg = '{}: {}'.format(type(err).__name__, str(err))
        variables = {'err': err_msg}
        arg = ''
    write_response(arg, variables)
    os.remove(data_json)


if __name__ == '__main__':
    main()
