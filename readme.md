Require: python3, tiktoken, openai,...
A simple Python script to call OpenAI API to translate .md, .txt files from Japanese to Vietnamese
- The program can translate .md, .txt files from Japanese to Vietnamese without losing the format such as tables, styles, etc. and automatically skip the unnecessary lines which does not contain Japanese characters that need to be translated to reduce the amount of token used.
- I have not made an GUI for this script.
How to run:
1, First you need to own a GPT-4 OpenAI account to be able to call the API without limitations
2, Add your OpenAI key to the apikey.py file
3, Change the input and output files
4, Run by command: python3 main.py, the result will be logged to the terminal
