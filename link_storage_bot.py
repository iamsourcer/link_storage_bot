import telebot
from telebot import types
import requests
import os
from datetime import date
#from readabilipy import simple_json_from_html_string
#from telegraph import Telegraph
#from telegraph.upload import upload_file
#from webpage2html import generate

TOKEN='1707490658:AAHB0YRnk0_TrV8vUur-TEjpEjbd60s13Lk'

bot = telebot.TeleBot(TOKEN, parse_mode=None)

#telegraph = Telegraph()
#telegraph.create_account(short_name='lsbot')

def parse_url_to_filename(url:str) -> str:
    name = url.replace('https://', '').replace('http://', '').replace('/', '___')
    # vamos a agregar un timestamp
    return f'{name}-{date.today()}'

def readability(url:str) -> dict:
    req = requests.get(url)
    article = simple_json_from_html_string(req.text, use_readability=True)
    return article

def telegraph_page(url:str):
    article = readability(url)
    response = telegraph.create_page(
        # esto debe tener fecha autor imagen y algo mas
        article['title'],
        html_content = '<br>'.join([p['text'] for p in article['plain_text']]),
        author_name = 'link_storage_bot'
        )
    return 'https://telegra.ph/{}'.format(response['path'])

def send_html(url, chat_id):
    name = parse_url_to_filename(url)

    #command = f'webpage2html {url}'
    #import subprocess
    #website = subprocess.check_output(command, shell=True) #could be anything here.

    command = f'webpage2html {url} > {name}.html'
    os.system(command)
    website = open(f'{name}.html', 'rb')

    #website = generate(url)

    bot.send_document(chat_id, website, caption=url)
    os.remove(website.name)
    return

def send_screenshot(url, chat_id, fullpage=False):

    name = parse_url_to_filename(url)
    if not fullpage:
        bot.send_message(chat_id, 'Generating capture...')
        capture = f'capture-website {url} --output=screenshots/{name}.png '
        os.system(capture)
        screenshot = open(f'screenshots/{name}.png', 'rb')
        bot.send_photo(chat_id, screenshot, caption=url)
        os.remove(screenshot.name)
    else:
        bot.send_message(chat_id, 'Generating full page capture, please wait...')
        capture = f'capture-website {url} --output=screenshots/{name}_full_page.jpeg  --full-page --type=jpeg --quality=0.1 '
        try:
            os.system(capture)
            full_screenshot = open(f'screenshots/{name}_full_page.jpeg', 'rb')
            bot.send_photo(chat_id, full_screenshot, caption=url)
            os.remove(full_screenshot.name)
        except Exception as e:
            print(e)
            bot.send_message(chat_id, 'Error while processing url')

def findUrlInMessage(message):
    for ent in message.entities:
        if ent.type == 'url':
            url = message.text[ent.offset: ent.offset + ent.length]
            return url

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome to Link Storage BOT!\n\nFeed me with an interesting URL and I'll keep it for YOU")

@bot.message_handler(func=lambda m: True)
def main_handler(message):
    url = findUrlInMessage(message)
    if not url:
        bot.send_message(message.chat.id, 'Please send me a valid URL')
        return
    send_html(url, message.chat.id)
    #send_screenshot(url, message.chat.id, fullpage=True)


if __name__ == '__main__':
    bot.polling(none_stop=True)

#bot.polling()

