import asyncio
import json
from pathlib import Path
import os
import re
import time

from dotenv import load_dotenv
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle

load_dotenv()

PROMPTS = [
    "Hi Bing, please describe the following links: ",
    'Try to write a wiki styled article with the topic ',
    'based on your ',
    'replies. Do not forget to keep all links as they are, including your suggested "learn more" section.',
    'Please inform me in some way if your response is too long for a single message, so we could continue the coversation.',
    "If you've reached the end of your response, plese inform me so I do not to prompt you further on this topic.",
    "Please format the article as Markdown.",
    'Please go on',
]

CHARACTER_LIMIT = 2048
THROTTLE = 20
DAILY_MAX = THROTTLE*10

n_out_of_m_regex = re.compile(r'[rR]esponse (\d) / (\d)')

def prepare_prompt(prompt_parts:list):
    prompt = ' '.join(prompt_parts)
    return prompt.strip()

async def bing_chat():
    Path(os.environ.get("SAVE_TO_FOLDER")).mkdir(parents=True, exist_ok=True)

    total_messages = 0
    chat_messages = 0
    topic_iterator = 3

    bookmarks_json = open('ordered_bookmarks.json', 'r')
    bookmarks_dictionary = json.load(bookmarks_json)
    bookmarks_json.close()
    
    bot = Chatbot()

    while total_messages < THROTTLE:
        current_topic = list(bookmarks_dictionary.keys())[topic_iterator]

        n,m = 0,0
        messages = []
        bing_chat = None
        try:
            for i in range(THROTTLE):
                prompt_parts = []
                if i == 0:
                    prompt_parts.append(PROMPTS[0])
                    prompt_parts.extend(bookmarks_dictionary[current_topic]['links'])
                    prompt_parts.append(PROMPTS[4])
                else:
                    if i == 0:
                        match_groups = n_out_of_m_regex.search(bing_chat['item']['messages'][2]['text'])
                    else:
                        match_groups = n_out_of_m_regex.search(bing_chat['item']['messages'][-1]['text'])
                
                    if match_groups is not None:
                        n,m = [int(i) for i in match_groups]
                    elif bing_chat['item']['messages'][-1]['text'].endswith('END'):
                        break
                    else:
                        n,m = 0,0

                    try:
                        if n % m != 0:
                            prompt_parts[PROMPTS[-1]]
                    except ZeroDivisionError:
                        prompt_parts.append(PROMPTS[1])
                        prompt_parts.append(f'"{current_topic}"')
                        prompt_parts.append(PROMPTS[2])
                        # how many messages it took to get the initial description
                        prompt_parts.append('1st')
                        if i == 2:
                            prompt_parts.append('to 2nd')
                        if i == 3:
                            prompt_parts.append('to 3rd')
                        if i > 3:
                            prompt_parts.append(f'to {i}th')
                        prompt_parts.append(PROMPTS[3])
                        prompt_parts.append(PROMPTS[4])
                        prompt_parts.append(PROMPTS[5])
                        prompt_parts.append(PROMPTS[6])

                prompt = prepare_prompt(prompt_parts)

                bing_chat = await bot.ask(prompt, conversation_style=ConversationStyle.creative)
                total_messages += 1

                for message in bing_chat['item']['messages']:
                    print(message['author'] + ":")
                    print(message['text'])
                    if len(messages) < i+1:
                        messages.append({})
                    messages[i][message['author']] = message['text']
                    

            chat_json = Path(os.environ.get("SAVE_TO_FOLDER"), f"chat-{'-'.join(time.asctime().split())}.json")
            with open(chat_json, 'w') as f:
                json.dump(messages, f, indent=5)

            bot.reset()

            with open('process_memory.json', 'rw') as f:
                topic_summary = {
                    ['topic']: current_topic,
                    ['daily_limit_used']: total_messages,
                    ['topic_end_time']: time.asctime(),
                }

                try:
                    process_memory = json.load(f)
                    process_memory['covered_topics'].append(topic_summary)
                except:
                    process_memory['covered_topics'] = [topic_summary]
                
                process_memory['last_iterator'] = topic_iterator
                process_memory['last_accessed'] = time.asctime()

                json.dump(process_memory, f)
                    
            topic_iterator += 1

        except BaseException as e:
            print(e)
            print(bing_chat)
            break

    await bot.close()
    


if __name__ == "__main__":
    asyncio.run(bing_chat())
