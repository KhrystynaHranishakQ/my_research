import os
from tika import parser
from dotenv import load_dotenv
from openai import OpenAI
import prompts

load_dotenv()

DATA_PATH = 'data/'
MODEL = "gpt-4-1106-preview"  # "gpt-3.5-turbo"
client = OpenAI()


def parse_file(file):
    # Tika can handle various file types, not just PDFs
    text = None
    try:
        file_data = parser.from_file(file)
        text = file_data['content'].strip().replace('/n/n', '')
        # logging.info("The file is parsed successfully")
    except Exception as e:
        print(str(e))
        # logging.error(f"File parsing error: {str(e)}")
    return text


def format_invoice_to_prompt(invoice):
    return f'"""{invoice}"""'


def get_gpt_response(system_message, user_message):

    response = None
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system",
                 "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        response = completion.choices[0].message.content
    except Exception as e:
        print(str(e))
        #logging.error(f"OpenAI API call error: {str(e)}")
    return response


if __name__ == '__main__':
    for file in sorted(os.listdir(DATA_PATH)):
        try:
            if file.split('.')[1] == 'pdf':
                text = parse_file(DATA_PATH + file)
                print(file)
                print('*' * 70)
                # print(text)
                # print('*'*70)
                user_prompt = format_invoice_to_prompt(text)
                gpt_response = get_gpt_response(prompts.system_definition, user_prompt)
                print(gpt_response)
                print('-'*70)
        except:
            print(f"Error with name: {file}")
            print('-' * 70)

