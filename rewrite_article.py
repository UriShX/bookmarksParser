import json
import time
from pathlib import Path
import re

import argparse

from helpers.file_helpers import check_dir_exists

# Parse the key from the command line
parser = argparse.ArgumentParser(description='Generate a markdown file from a key.')
parser.add_argument('key', type=str, help='The key of the article to generate.')
args = parser.parse_args()

def load_bookmarks_and_axtract_paths(key:str):
    with open('ordered_bookmarks.json', 'r') as f:
        bookmarks = json.load(f)
    category = "Private Bookmarks" if "Private Bookmarks" in bookmarks[key]['path'][0] else "Work Bookmarks"
    parent_folder = '-' #'bookmarks[key]['path'][0][-2]'
    for i in range(len(bookmarks[key]['path'][0])):
        parent_folder = bookmarks[key]['path'][0][i] if len(bookmarks[key]['path'][0]) - i == 2 else parent_folder
    children_folders = bookmarks[key]['children']
    return category, parent_folder, children_folders

def load_wiki_article_and_link_descriptions(key):
    # Load the contents of jekyll_wiki_article.md
    key = key.replace('/', '_')
    with open(Path('./generated_articles', f'{key}_wiki_article.md'), 'r') as f:
        wiki_article = f.read()
    # Load the contents of jekyll_link_descriptions.md
    with open(Path('./link_descriptions', f'{key}_link_descriptions.md'), 'r') as f:
        link_descriptions = f.read()
    return wiki_article, link_descriptions

def replace_links_with_descriptions(key, wiki_article, link_descriptions):
    # Replace the 'important links' section with the contents of jekyll_link_descriptions.md
    wiki_article_list = wiki_article.split(re.search(r'[#* ]+Important Links:?[#*]*\s', wiki_article).group(0))
    link_descriptions_list = link_descriptions.split(f'---\n')
    wiki_article_list[1] = link_descriptions_list[2]
    wiki_article = '## Important Links\n\n'.join(wiki_article_list)
    return wiki_article


def add_front_matter_and_folders(wiki_article, key, category, parent_folder, children_folders):
    # Add front matter that indicates the content is AI generated
    front_matter = f"""---
# layout: post
title:  "{key}"
date:   {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
categories: {category}
ai_generated: true
---
"""
    wiki_article = front_matter + f"\n\n## Folders\nParent folder: [[{parent_folder}]]\n\nChildren folders: [[{']], [['.join(children_folders)}]]\n\n" + wiki_article
    wiki_article = wiki_article + "## Footnotes:\n"
    return wiki_article

def main(key):
    category, parent_folder, children_folders = load_bookmarks_and_axtract_paths(key)
    wiki_article, link_descriptions = load_wiki_article_and_link_descriptions(key)
    wiki_article = replace_links_with_descriptions(key, wiki_article, link_descriptions)
    wiki_article = add_front_matter_and_folders(wiki_article, key, category, parent_folder, children_folders)
    # Save the generated markdown file as Jekyll.md
    check_dir_exists('./edited_articles')
    key = key.lower().replace(' ', '-').replace('/', '_')
    with open(Path('./edited_articles', f'{key}.md'), 'w') as f:
        f.write(wiki_article)


if __name__ == '__main__':
    main(args.key)
