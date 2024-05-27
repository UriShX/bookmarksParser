"""
This script is used to parse JSON responses to markdown files.
The script takes a JSON file as input, extracts the necessary information, and writes it to a markdown file.
The JSON file contains data in a specific format, and the script processes it to generate a markdown file with formatted content.
The script is run from the command line, with the filename of the JSON file as the argument.
The generated markdown file will have the same name as the JSON file, but with the .md extension.
This script is specifically designed to parse link descriptions from a JSON file and convert them to markdown format.
"""
import json
from pathlib import Path
import re

import argparse

from helpers.file_helpers import check_dir_exists

footnote_regex = re.compile(r'\[\^(\d+)\^\]')

# Parse the filename from the command line, and target directory
parser = argparse.ArgumentParser(description='Parse link descriptions to markdown.')
parser.add_argument('filename', type=str, help='The filename of the json file containing the link descriptions.')
parser.add_argument('--wiki', action='store_true', help='Parse a wiki article instead of link descriptions.')
parser.add_argument('--links', action='store_true', help='Parse link descriptions instead of a wiki article.')
args = parser.parse_args()

def parse_wiki_article_to_md(filename):
    """
    Parse the wiki article from the wiki.json file to a markdown file.

    Args:
        filename (str): The filename of the json file containing the wiki article.

    Returns:
        None
    """
    check_dir_exists('./generated_articles')
    md_filename = Path(filename).with_suffix('.md')
    md_filename = Path('./generated_articles', md_filename.name)
    filename = Path(filename)
    with open(filename, 'r') as f:
        data = json.load(f)
    with open(md_filename, 'w') as f:
        # for i, response in enumerate(data):
            message = data["item"]["result"]["message"]
            f.write(f"{message}\n\n")
    
    print(f"Markdown file written to {md_filename}")


def parse_link_descriptions_to_md(filename):
    """
    Parse the link descriptions from the links.json file to a markdown file.

    Args:
        filename (str): The filename of the json file containing the link descriptions.

    Returns:
        None
    """
    check_dir_exists('./link_descriptions')
    md_filename = Path(filename).with_suffix('.md')
    md_filename = Path('./link_descriptions', md_filename.name)
    filename = Path(filename)
    with open(filename, 'r') as f:
        data = json.load(f)
    with open(md_filename, 'w') as f:
        f.write(f'---\ntitle: {filename.stem}\n---\n')
        for i, link in enumerate(data.keys()):
            message = data[link]["item"]["result"]["message"]
            attributions_list = []
            for m in data[link]["item"]["messages"]:
                try:
                    atttribution = m["sourceAttributions"]
                    attributions_list.extend(atttribution)
                except KeyError:
                    pass
            list_footnotes = list(footnote_regex.findall(message))
            # print(list_footnotes)
            # replace the footnotes with the correct numbering
            unique_footnotes = sorted(set(list_footnotes))
            for j, footnote in enumerate(unique_footnotes):
                message = message.replace(f'[^{footnote}^]', f'[^{i+1}-{j+1}]')

            f.write(f"- ### {link}\n\n")
            f.write(f"\t{message}\n\n")
            # print(attributions_list)
            for j, attribution in enumerate(attributions_list):
                # print(f"{i+1}.{j+1}: {attribution}")
                if "IsCitedInResponse" in attribution.keys() and attribution["IsCitedInResponse"]== "True":
                    f.write('\t[^{}-{}]:({}) {}\n\n'.format(i+1, j+1, attribution['seeMoreUrl'], attribution['providerDisplayName']))
    
    print(f"Markdown file written to {md_filename}")


if __name__ == "__main__":
    # Check wether to parse a wiki article or link descriptions
    if args.wiki:
        parse_wiki_article_to_md(args.filename)
    elif args.links:
        parse_link_descriptions_to_md(args.filename)
    else:
        print("Please specify whether to parse a wiki article or link descriptions.")
        print("Use the --wiki flag to parse a wiki article.")
        print("Use the --links flag to parse link descriptions.")
        print("Example: python parse_json_responses_to_md.py links.json --links")
        print("Example: python parse_json_responses_to_md.py wiki.json --wiki")
        print("Exiting...")
        exit(1)
