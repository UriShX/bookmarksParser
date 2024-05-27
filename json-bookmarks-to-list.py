import os
import json
from dotenv import load_dotenv
import helpers.dict_helpers as dict_helpers

load_dotenv()

bookmarks_json = open(os.environ.get("BOOKMARKS_FILE"))
bookmarks_dict = json.load(bookmarks_json)
bookmarks_json.close()

urls = dict_helpers.get_recursively(bookmarks_dict, 'url')

ordered_dict = {}

for url in urls:
    lst = dict_helpers.breadcrumb(bookmarks_dict, url)

    bookmark_path = []
    bookmark_name = ''

    for i in range(len(lst)):
        if lst[i] == 'children':
            bookmark_path.append(dict_helpers.get_nested(lst[:i], bookmarks_dict)['name'])
        elif lst[i] == 'url':
            bookmark_name = dict_helpers.get_nested(lst[:i], bookmarks_dict)['name']

    bookmark_link = f'[{bookmark_name}]({url})' if not bookmark_name == '' else f'({url})'

    for i in range(len(bookmark_path)):
        if bookmark_path[i] == 'Bookmarks':
            bookmark_path[i] = os.environ.get("BOOKMARKS_TAG") + ' ' + bookmark_path[i]
    
    folder_name = bookmark_path[-1]
    parent = bookmark_path[-2] if len(bookmark_path) > 1 else None
    # bookmark_path = ' > '.join(bookmark_path)

    if folder_name in ordered_dict.keys():
        if 'links' not in ordered_dict[folder_name]:
            ordered_dict[folder_name]['links'] = []
        ordered_dict[folder_name]['links'].append(bookmark_link)
        if bookmark_path not in ordered_dict[folder_name]['path']:
            ordered_dict[folder_name]['path'].append(bookmark_path)
    else:
        ordered_dict[folder_name] = {'links':[bookmark_link], 'path':[bookmark_path], 'children':[]}

    if parent is not None:
        if parent not in ordered_dict.keys():
            ordered_dict[parent] = {'links':[],'path':[],'children':[]}

        if folder_name not in ordered_dict[parent]['children']:
            ordered_dict[parent]['children'].append(folder_name)

    # print(bookmark_path)

with open('ordered_bookmarks.json', 'w') as f:
    json.dump(ordered_dict, f, indent=5)