import os
import json
from pathlib import Path
import subprocess
import re


def get_data_json():
    return Path(os.environ['cachedir']) / 'curr_data.json'


def request_pandoc(html: str):
    return subprocess.run(['pandoc', '-f', 'html', '-t', 'markdown'],
                          input=html,
                          capture_output=True,
                          text=True,
                          check=True).stdout


def repl_inline_math(matchobj: re.Match):
    math_expr = matchobj.group(1)
    if math_expr.startswith('\\\\('):
        math_expr = math_expr[3:]
    if math_expr.endswith('\\\\)'):
        math_expr = math_expr[:-3]
    math_expr = math_expr.replace('\\^', '^').replace('\\\\', '\\')
    return '${}$'.format(math_expr)


def repl_block_math(matchobj: re.Match):
    math_expr = matchobj.group(1)
    math_expr = re.sub(r'\\([$^_\\])', r'\1', math_expr)
    return math_expr


def repl_block_code(matchobj: re.Match):
    block = matchobj.group(1)
    block = ''.join(s[4:] if s.startswith('    ') else s
                   for s in re.findall(r'.*\n', block))
    return '```\n{}```'.format(block)


def text_fix(text: str):
    """Fix errors in math and code blocks"""
    text = re.sub(r'\[(.+?)\]\{\.math\}', repl_inline_math, text)
    text = re.sub(r'::: math\n(.+?)\n:::', repl_block_math, text, flags=re.DOTALL)
    text = re.sub(r'::: highlight\n(.+?):::', repl_block_code, text, flags=re.DOTALL)
    text = re.sub(r'::: style\n(.+?):::', r'\1', text, flags=re.DOTALL)
    text = text.replace("\\'", "'")
    text = text.replace('\\"', '"')
    return text


def test_text_fix():
    old = r'Gumbel-max requires [\\(K\\)]{.math} samples from a uniform'
    assert text_fix(old) == 'Gumbel-max requires $K$ samples from a uniform'
    old = '::: highlight\n    def usual(x):\n        z = cdf[-1]\n:::'
    assert text_fix(old) == '```\ndef usual(x):\n    z = cdf[-1]\n```'
    old = '::: math\n\\$\\$ y = \\\\underset{ i \\\\in \\\\{1,\\\\cdots,K\\\\} }{\\\\operatorname{argmax}}\nx_i + z_i \\$\\$\n:::'
    assert text_fix(old) == '$$ y = \\underset{ i \\in \\{1,\\cdots,K\\} }{\\operatorname{argmax}}\nx_i + z_i $$'
    old = r'''::: math
\$\$ \\pi_k = \\frac{1}{z} \\exp(x_k) \\ \\ \\ \\text{where } z =
\\sum\_{j=1}\^K \\exp(x_j) \$\$
:::'''
    assert text_fix(old) == r'''$$ \pi_k = \frac{1}{z} \exp(x_k) \ \ \ \text{where } z =
\sum_{j=1}^K \exp(x_j) $$'''


def generate_article(article_data: dict):
    md = text_fix(request_pandoc(article_data['html']).strip())
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


def main():
    data_json = get_data_json()
    with open(data_json, encoding='utf-8') as infile:
        article_data = json.load(infile)
    print(generate_article(article_data), end='')
    os.remove(data_json)


if __name__ == '__main__':
    main()
