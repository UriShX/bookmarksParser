# bookmarksParser
A collection of python scripts to parse bookmarks files, then get an AI to generate some wiki pages from them.

## Usage
### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Edit '.env' file
```bash
cp .env.example .env
```
Edit the '.env' file to set the path to your bookmarks file.

### 3. Run 'json-bookmarks-to-list.py'
```bash
python json-bookmarks-to-list.py
```
This script will parse the bookmarks file and generate a list of bookmarks in a JSON file.

### 4. Run 'copilot_chat.py'
Open the generated JSON file and select one of the folders to generate a wiki page from. Then run the following command:
```bash
python copilot_chat.py 'bookmark folder name'
```

### 5. Run 'rewrite_article.py'
```bash
python rewrite_article.py 'bookmark folder name'
```

## TODO
- [ ] Automate the process of generating wiki pages from bookmarks
- [ ] Create a cli to interact with the scripts - display and select bookmarks folders, generate wiki pages, etc.
- [ ] Add an easy way to detect bookmarks update, without rewriting the whole wiki page
- [ ] Add a way to create a RAG for querying the generated articles