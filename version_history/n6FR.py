import openai
import re
import tiktoken
import time
import unicodedata
# import os
# import logging
# from logging.handlers import TimedRotatingFileHandler
# from datetime import datetime

# def getLogger():
#     logger = logging.getLogger(__name__)
#     logger.setLevel(logging.INFO)

#     formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

#     handler = TimedRotatingFileHandler(os.path.join('./logs/', 'translate.log'), 
#                             when='midnight', backupCount=7)
#     handler.setLevel(logging.DEBUG)
#     handler.setFormatter(formatter)

#     logger.addHandler(handler)

#     return logger

# logger = getLogger()

prompt_template = """
You are a FROM_LANG to TO_LANG translator in the IT field.
Translate the content below into TO_LANG in the style used in IT.
The content to be translated in one sentence will follow the format below, I will send multiple sentences in one message:
“&line number& {{sentence to be translated in Japanese}}”
Please reply with the format:
“&line number& {{Vietnamese sentence}}”
rules: must keep the number of lines between &number& are line breaks then keep them, if there are nothing to translate still keep the number of lines inside square, also keep all the special characters including spaces;
never translate SQL queries (start with FROM, SELECT, and all...);
Please translate the entire message into TO_LANG with the same format as above, if you can't translate, leave the content behind the mark blank. If the content to be translated contains TO_LANG, that TO_LANG phrase does not need to be translated.
Here is the text need to be translated:
"""

input_path = "/home/phuongthao/TranslateTool/Data/sample-with-code.md"
output_path = "/home/phuongthao/TranslateTool/Data/output.md"

def generate_prompt(from_lang, to_lang):
    if from_lang == 'all':
        from_lang = 'any language'
    return prompt_template.replace('FROM_LANG', from_lang).replace('TO_LANG', to_lang)

MAX_TOKENS_LENGTH = 2048

def contains_cjk(text):
    for character in text:
        name = unicodedata.name(character, None)
        if name and ('CJK UNIFIED' in name or 'HIRAGANA' in name or 'KATAKANA' in name):
            return True
    return False

def num_tokens_from_string(string: str, encoding_name:str = "gpt-3.5-turbo") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def is_valid_token_length(user_input: str):
    return num_tokens_from_string(prompt_template) + num_tokens_from_string(user_input) <= MAX_TOKENS_LENGTH

def is_need_translate(input: str, from_lang: str):
    if isinstance(input, str):
        if re.search(r"^=.+", input):
                return False
        if from_lang != 'japanese':
            return True
        elif contains_cjk(input):
            return True
    return False

def openai_translate(content: str, from_lang: str, to_lang: str):
    # start = time.time()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": generate_prompt(from_lang, to_lang)},
                {"role": "user", "content": content},
            ]
    )
    end = time.time()
    # logger.info (f"Api call time elapsed: {end - start}")
    return {
        "content": response['choices'][0]['message']['content'],
        "total_tokens": response['usage']['total_tokens']
    }

def translate(input_path: str, output_path: str, from_lang: str, to_lang: str):
    input = open(input_path)
    output = open(output_path,"w+")
    output.write(input.read())
    line_accumulator=""
    input.seek(0)
    for line_num, line in enumerate(input, start=1):
        if line != "\n" and is_need_translate(line, from_lang) and is_valid_token_length(prompt_template + line_accumulator):
            line_accumulator+=(f"&{line_num}& {line}")
        else:
            continue
    output.close()
    response_results = openai_translate(prompt_template + line_accumulator, from_lang, to_lang)
    print(response_results['total_tokens'])
    for line in response_results['content'].splitlines():
        numbers = re.findall(r'\&(\d+)\&', line )
        new_content = re.sub(r'\&\d+\&', '', line).strip()
        with open(output_path, 'r') as file:
            lines = file.readlines()
        if int(numbers[0]) <= len(lines):
            lines[int(numbers[0]) - 1] = new_content + '\n' 
            with open(output_path, 'w') as file:
                file.writelines(lines)
            print("Line content changed successfully.")
        else:
            print("Line number is out of range.")

translate(input_path, output_path, 'Japanese', 'Vietnamese')