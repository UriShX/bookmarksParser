import asyncio
from typing import Optional, List, Dict, AnyStr, SupportsInt, SupportsFloat
import argparse
import json


# Parse the function from the command line.
# Available functions are: 
# - load_and_order_bookmarks
# - display_bookmark_folders
# - example_explain_link
# - example_chat
# - create_complete_wiki_article
parser = argparse.ArgumentParser(description='Run a function.')
parser.add_argument('function', type=str, help='The function to run.')
args = parser.parse_args()

async def get_input():
    return await asyncio.get_event_loop().run_in_executor(None, input, "type something: ")

async def main():
    while True:
        user_input:AnyStr = await get_input()
        if user_input == "exit":
            break
        print(f"User entered: {user_input}")

if __name__ == "__main__":
    asyncio.run(main())