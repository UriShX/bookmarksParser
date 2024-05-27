import markdown
import os
import json
from pathlib import Path
import argparse

# parse the filename or path from the command line
parser = argparse.ArgumentParser(description='Parse markdown to json.')
parser.add_argument('filename', type=str, help='The filename or path of the markdown file to parse.')
args = parser.parse_args()

def markdown_to_json(md_file_path):
    with open(md_file_path, 'r') as file:
        text = file.read()
    md = markdown.Markdown(extensions=['meta'])
    html = md.convert(text)
    print(md.Meta)
    data = {
        'title': md.Meta.get('title', [''])[0],
        'content': html
    }
    json_path = md_file_path.replace('.md', '.json')
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file)

def convert_md_files_in_path(path):
    for md_file in os.listdir(path):
        if md_file.endswith('.md'):
            markdown_to_json(os.path.join(path, md_file))

if __name__ == '__main__':
    # check if the input is a file or a path
    if os.path.isfile(args.filename):
        markdown_to_json(args.filename)
    elif os.path.isdir(args.filename):
        convert_md_files_in_path(args.filename)
    else:
        print('Invalid input. Please provide a valid file or path.')
