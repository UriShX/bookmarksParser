"""
Copilot chat script, translated from bing_chat.py to use sydney-py instead of edgegpt
"""
import asyncio
import json
from pathlib import Path
import os
import re
import time

import argparse

from dotenv import load_dotenv
from sydney import SydneyClient

from helpers.file_helpers import check_dir_exists
from parse_json_responses_to_md import parse_link_descriptions_to_md, parse_wiki_article_to_md

load_dotenv()

# parse the key from the command line
parser = argparse.ArgumentParser(description='Generate a markdown file from a key.')
parser.add_argument('key', type=str, help='The key of the article to generate.')
parser.add_argument('--context', nargs='+', help='The context path of the article.')
parser.add_argument('--subfolders', nargs='+', help='The subfolders of the article.')
parser.add_argument('--links_only', action='store_true', help='Parse link descriptions without writing a wiki article.')
args = parser.parse_args()

async def write_wiki(key:str, context_path:list=None, context_subfolders:list=None) -> None:
    prompt = []
    md_descritions = ""

    filekey = key.replace('/', '_')
    check_dir_exists('./link_descriptions')
    with open(Path('./link_descriptions', f'{filekey}_link_descriptions.md'), 'r') as f:
        md_descritions = f.read()
    
    prompt.append('Hi Copilot, please write a wiki styled article with the topic of "{key}" based on the following descriptions:')
    prompt.append(md_descritions)
    prompt.append('The links and descriptions will be attached in a section named "important links" as they are presented to you by me. Please do not rewrite them.')
    prompt.append('The article is for my personal wiki, supplementing my zettlekasten system. The links are from my browser bookmarks, which are organized in folders.')
    if context_path is not None:
        prompt.append(f'For added context, the path to the this topic is: {" -> ".join(context_path)}')
    if context_subfolders is not None:
        prompt.append(f'And the subfolders are: {", ".join(context_subfolders)}')
    prompt.append('Do not forget to keep all links as they are, including your suggested "learn more" section. Double check yourself')
    prompt.append('Please inform me in some way if your response is too long for a single message, so we could continue the conversation.')
    prompt.append('If you\'ve reached the end of your response, please inform me so I do not to prompt you further on this topic.')
    prompt = ' '.join(prompt)
    
    async with SydneyClient() as sydney:
        response = await sydney.compose(prompt, tone="informational", length="short", format="paragraph", suggestions=True, raw=True)
        print(response)
        check_dir_exists('./chats')
        with open(Path('./chats', f'{filekey}_wiki_article.json'), 'w') as f:
            json.dump((response[0]), f, indent=5)


async def explain_links(key:str) -> None:
    bookmarks_folder = json.load(open('ordered_bookmarks.json', 'r'))
    context_path = bookmarks_folder[key]['path'][0]
    context_subfolders = bookmarks_folder[key]['children']

    prompt = []
    prompt.append("Hi Copilot, please describe the following link.")
    if len(context_path) > 0:
        prompt.append(f"The link is from my broswer bookmarks, under the folder {' -> '.join(context_path)}.")
    prompt.append("Please respond in a two to three sentences long paragraph. Link:")
    prompt = ' '.join(prompt)
    responses = {}
    
    for link in bookmarks_folder[key]['links']:
        async with SydneyClient(style="precise") as sydney:
            response = await sydney.ask(prompt, context=link, raw=True)
            # print(response)
            responses[link] = response
            check_dir_exists('./chats')
            key = key.replace('/', '_')
            with open(Path('./chats', f'{key}_link_descriptions.json'), 'w') as f:
                json.dump(responses, f, indent=5)

    return {"success": True, "context_path": context_path, "context_subfolders": context_subfolders}


if __name__ == "__main__":
    if args.key is None:
        raise ValueError("Please provide a key.")
        exit(1)
    
    explained = asyncio.run(explain_links(args.key))
    key = args.key.replace('/', '_')
    check_dir_exists('./chats')
    parse_link_descriptions_to_md(Path('./chats', f'{key}_link_descriptions.json'))
    if not args.links_only:
        asyncio.run(write_wiki(args.key, context_path=args.context if args.context is not None else explained["context_path"], context_subfolders=args.subfolders if args.subfolders is not None else explained["context_subfolders"]))
    parse_wiki_article_to_md(Path('./chats',f'{key}_wiki_article.json'))
    # asyncio.run(explain_links("Gems"))
